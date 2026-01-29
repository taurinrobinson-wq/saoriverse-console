{ pkgs }: {
  deps = [
    pkgs.python313
    pkgs.python313Packages.pip
    pkgs.nodejs_20
    pkgs.bash
  ];
  
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.python313
    ];
    PYTHONBIN = "${pkgs.python313}/bin/python3";
    LANG = "en_US.UTF-8";
    LC_ALL = "en_US.UTF-8";
  };
}
