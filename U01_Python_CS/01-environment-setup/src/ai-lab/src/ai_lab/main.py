import numpy as np
import check_version 

for pkg in ("numpy", "pandas", "matplotlib"):
      print(f"  {pkg:<12}: {check_version.check_pkg(pkg)}")

check_version.check_device()