{ pkgs }: {
  deps = [
    pkgs.python313
    pkgs.python313Packages.fastapi
    pkgs.python313Packages.uvicorn
    pkgs.python313Packages.pydantic
    pkgs.python313Packages.pyyaml
    pkgs.python313Packages.python-docx
  ];
}
