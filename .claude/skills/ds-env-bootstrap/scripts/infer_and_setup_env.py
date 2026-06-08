from __future__ import annotations

import argparse
import re
import subprocess
import sys
import textwrap
import tempfile
import venv
import zipfile
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


BASE_PACKAGES = {
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "jupyter",
    "ipykernel",
    "scikit-learn",
}

KEYWORD_PACKAGE_MAP = {
    "xgboost": {"xgboost"},
    "lightgbm": {"lightgbm"},
    "optuna": {"optuna"},
    "shap": {"shap"},
    "gridsearchcv": {"scikit-learn"},
    "stratifiedkfold": {"scikit-learn"},
    "pipeline": {"scikit-learn"},
    "columntransformer": {"scikit-learn"},
    "notebook": {"jupyter", "ipykernel"},
    "kaggle": {"kaggle"},
    "plotly": {"plotly"},
    "scipy": {"scipy"},
    "chi-cuadrado": {"scipy"},
    "point-biserial": {"scipy"},
    "pdf": {"reportlab"},
}

RISKY_BY_DEFAULT = {"lightgbm", "xgboost", "shap", "fairlearn"}

WINDOWS_RISKY = {"lightgbm"}


def run_command(command: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=check, text=True, capture_output=True)


def read_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as docx_zip:
        xml_content = docx_zip.read("word/document.xml")
    root = ET.fromstring(xml_content)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for paragraph in root.findall(".//w:p", namespace):
        text_chunks = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        merged = "".join(text_chunks).strip()
        if merged:
            paragraphs.append(merged)
    return "\n".join(paragraphs)


def read_spec_text(spec_path: Path) -> str:
    suffix = spec_path.suffix.lower()
    if suffix == ".docx":
        return read_docx_text(spec_path)
    return spec_path.read_text(encoding="utf-8", errors="ignore")


def infer_packages(spec_text: str) -> list[str]:
    normalized_text = spec_text.lower()
    inferred = set(BASE_PACKAGES)

    for keyword, packages in KEYWORD_PACKAGE_MAP.items():
        if keyword in normalized_text:
            inferred.update(packages)

    # Heuristic: if fairness or bias terms appear, add metrics helper.
    if re.search(r"\bfairness\b|\bsesgo\b|\bequal opportunity\b|\bdemographic parity\b", normalized_text):
        inferred.add("fairlearn")

    # Heuristic: if "dashboard" or "streamlit" appears, include streamlit.
    if re.search(r"\bdashboard\b|\bstreamlit\b", normalized_text):
        inferred.add("streamlit")

    return sorted(inferred)


def split_packages_by_risk(packages: list[str]) -> tuple[list[str], list[str]]:
    safe_packages = []
    risky_packages = []
    for package in packages:
        risky = package in RISKY_BY_DEFAULT
        if sys.platform.startswith("win") and package in WINDOWS_RISKY:
            risky = True
        if risky:
            risky_packages.append(package)
        else:
            safe_packages.append(package)
    return sorted(set(safe_packages)), sorted(set(risky_packages))


def ensure_venv(venv_path: Path) -> Path:
    if not venv_path.exists():
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(venv_path)

    if sys.platform.startswith("win"):
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"

    if not python_path.exists():
        raise FileNotFoundError(f"No se encontro el Python del entorno en: {python_path}")
    return python_path


def write_requirements(requirements_path: Path, packages: Iterable[str]) -> None:
    requirements_path.write_text("\n".join(sorted(set(packages))) + "\n", encoding="utf-8")


def parse_requirement_names(requirements_path: Path) -> list[str]:
    package_names: list[str] = []
    for line in requirements_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        candidate = line.strip()
        if not candidate or candidate.startswith("#") or candidate.startswith("-"):
            continue
        match = re.match(r"^([A-Za-z0-9_.-]+)", candidate)
        if match:
            package_names.append(match.group(1).lower())
    return sorted(set(package_names))


def freeze_lockfile(venv_python: Path, lock_path: Path) -> subprocess.CompletedProcess:
    freeze = run_command([str(venv_python), "-m", "pip", "freeze", "--exclude-editable"], check=False)
    if freeze.returncode == 0:
        lock_path.write_text((freeze.stdout or "").strip() + "\n", encoding="utf-8")
    return freeze


def verify_imports(venv_python: Path, packages: list[str]) -> tuple[bool, str]:
    import_targets = []
    for package in packages:
        if package == "scikit-learn":
            import_targets.append("sklearn")
        elif package == "ipykernel":
            import_targets.append("ipykernel")
        elif package == "jupyter":
            continue
        else:
            import_targets.append(package.replace("-", "_"))

    script = "import importlib\n" + "\n".join(
        [f"importlib.import_module('{target}')" for target in sorted(set(import_targets))]
    ) + "\nprint('IMPORT_CHECK_OK')\n"

    result = run_command([str(venv_python), "-c", script], check=False)
    return (result.returncode == 0, (result.stdout or "") + (result.stderr or ""))


def write_report(
    report_path: Path,
    venv_path: Path,
    mode: str,
    lock_path: Path,
    installed_packages: list[str],
    skipped_risky_packages: list[str],
    import_ok: bool,
    import_log: str,
) -> None:
    status = "OK" if import_ok else "CON_OBSERVACIONES"
    skipped_text = (
        "\n".join([f"- {pkg}" for pkg in skipped_risky_packages])
        if skipped_risky_packages
        else "- Ninguna"
    )
    report = f"""# Setup Environment Report

- Entorno: `{venv_path}`
- Modo: `{mode}`
- Lockfile: `{lock_path}`
- Estado de imports: **{status}**

## Dependencias top-level
{chr(10).join([f"- {pkg}" for pkg in installed_packages])}

## Dependencias omitidas por robustez (modo alumno)
{skipped_text}

## Log de verificacion
```text
{import_log.strip() or "Sin salida"}
```
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepara entorno Python reproducible con lockfile congelado."
    )
    parser.add_argument("--env-name", default=".venv", help="Nombre/ruta del entorno virtual.")
    parser.add_argument(
        "--requirements",
        default="requirements.txt",
        help="Ruta del lockfile de salida/entrada (versiones exactas).",
    )
    parser.add_argument(
        "--base-requirements",
        default="requirements.in",
        help="Ruta de dependencias base (sin pin) para generar lockfile.",
    )
    parser.add_argument(
        "--bootstrap-spec",
        help="Opcional: consigna para bootstrap inicial SOLO si no existe base-requirements.",
    )
    parser.add_argument("--report", default="reports/setup_env_report.md", help="Ruta del reporte de setup.")
    parser.add_argument(
        "--refresh-lock",
        action="store_true",
        help="Regenera lockfile desde base-requirements o bootstrap-spec.",
    )
    parser.add_argument(
        "--allow-risky",
        action="store_true",
        help="Solo para bootstrap-spec: incluye paquetes conflictivos.",
    )
    args = parser.parse_args()

    venv_path = Path(args.env_name).resolve()
    lock_path = Path(args.requirements).resolve()
    base_requirements_path = Path(args.base_requirements).resolve()
    report_path = Path(args.report).resolve()

    venv_python = ensure_venv(venv_path)
    run_command([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
    skipped_risky_packages: list[str] = []
    mode = "locked-install"
    top_level_packages: list[str] = []

    if lock_path.exists() and not args.refresh_lock:
        install = run_command([str(venv_python), "-m", "pip", "install", "-r", str(lock_path)], check=False)
        if base_requirements_path.exists():
            top_level_packages = parse_requirement_names(base_requirements_path)
        else:
            top_level_packages = parse_requirement_names(lock_path)
        freeze = run_command(["python", "-c", "print('LOCK_REUSED')"], check=False)
    else:
        mode = "lock-regenerated"
        if base_requirements_path.exists():
            top_level_packages = parse_requirement_names(base_requirements_path)
            install = run_command(
                [str(venv_python), "-m", "pip", "install", "-r", str(base_requirements_path)],
                check=False,
            )
        elif args.bootstrap_spec:
            spec_path = Path(args.bootstrap_spec).resolve()
            if not spec_path.exists():
                raise FileNotFoundError(f"No existe la consigna: {spec_path}")
            spec_text = read_spec_text(spec_path)
            inferred_packages = infer_packages(spec_text)
            safe_packages, risky_packages = split_packages_by_risk(inferred_packages)
            top_level_packages = inferred_packages if args.allow_risky else safe_packages
            skipped_risky_packages = [] if args.allow_risky else risky_packages
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as temp_req:
                temp_req.write("\n".join(top_level_packages) + "\n")
                temp_path = temp_req.name
            install = run_command(
                [str(venv_python), "-m", "pip", "install", "-r", temp_path],
                check=False,
            )
            if not base_requirements_path.exists():
                write_requirements(base_requirements_path, top_level_packages)
        else:
            raise FileNotFoundError(
                "No hay lockfile ni base-requirements. Proveé requirements.in o --bootstrap-spec."
            )

        freeze = freeze_lockfile(venv_python, lock_path)
        if freeze.returncode != 0:
            raise RuntimeError(f"No se pudo generar lockfile en {lock_path}")

    import_ok, import_log = verify_imports(venv_python, top_level_packages)
    full_log = textwrap.dedent(
        f"""
        [mode]
        {mode}

        [pip install]
        returncode={install.returncode}
        {install.stdout}
        {install.stderr}

        [lock freeze]
        returncode={freeze.returncode}
        {freeze.stdout}
        {freeze.stderr}

        [import check]
        {import_log}

        [skipped risky]
        {", ".join(skipped_risky_packages) if skipped_risky_packages else "none"}
        """
    ).strip()
    write_report(
        report_path,
        venv_path,
        mode,
        lock_path,
        top_level_packages,
        skipped_risky_packages,
        import_ok and install.returncode == 0,
        full_log,
    )

    print("SETUP_DONE")
    print(f"requirements_lock: {lock_path}")
    print(f"requirements_base: {base_requirements_path}")
    print(f"report: {report_path}")
    if skipped_risky_packages:
        print(f"SKIPPED_RISKY: {', '.join(skipped_risky_packages)}")
    if install.returncode != 0 or not import_ok:
        print("SETUP_WITH_WARNINGS")


if __name__ == "__main__":
    main()
