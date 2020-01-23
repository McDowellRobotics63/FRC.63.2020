set -e
PACKAGES=()
DO_INSTALL=0
if ! opkg list-installed | grep -F 'libgfortran3 - 6.3.0-r0'; then
    PACKAGES+=("opkg_cache/libgfortran3_6.3.0-r0_cortexa9-vfpv3.ipk")
    DO_INSTALL=1
else
    echo "libgfortran3 already installed"
fi
if ! opkg list-installed | grep -F 'python37 - 3.7.2-r0'; then
    PACKAGES+=("opkg_cache/python37_3.7.2-r0_cortexa9-vfpv3.ipk")
    DO_INSTALL=1
else
    echo "python37 already installed"
fi
if ! opkg list-installed | grep -F 'libgcc1 - 6.3.0-r0.14'; then
    PACKAGES+=("opkg_cache/libgcc1_6.3.0-r0.14_cortexa9-vfpv3.ipk")
    DO_INSTALL=1
else
    echo "libgcc1 already installed"
fi
if ! opkg list-installed | grep -F 'libstdc++6 - 6.3.0-r0.13'; then
    PACKAGES+=("opkg_cache/libstdc++6_6.3.0-r0.13_cortexa9-vfpv3.ipk")
    DO_INSTALL=1
else
    echo "libstdc++6 already installed"
fi
if ! opkg list-installed | grep -F 'ATLAS - 3.10.3'; then
    PACKAGES+=("opkg_cache/ATLAS_3.10.3_cortexa9-vfpv3.ipk")
    DO_INSTALL=1
else
    echo "ATLAS already installed"
fi
if ! opkg list-installed | grep -F 'opencv3 - 3.4.5-r0'; then
    PACKAGES+=("opkg_cache/opencv3_3.4.5-r0_cortexa9-vfpv3.ipk")
    DO_INSTALL=1
else
    echo "opencv3 already installed"
fi
if ! opkg list-installed | grep -F 'python37-numpy - 1.15.4'; then
    PACKAGES+=("opkg_cache/python37-numpy_1.15.4_cortexa9-vfpv3.ipk")
    DO_INSTALL=1
else
    echo "python37-numpy already installed"
fi
if ! opkg list-installed | grep -F 'python37-opencv3 - 3.4.5-r0'; then
    PACKAGES+=("opkg_cache/python37-opencv3_3.4.5-r0_cortexa9-vfpv3.ipk")
    DO_INSTALL=1
else
    echo "python37-opencv3 already installed"
fi
if ! opkg list-installed | grep -F 'python37-robotpy-cscore - 2019.1.0'; then
    PACKAGES+=("opkg_cache/python37-robotpy-cscore_2019.1.0_cortexa9-vfpv3.ipk")
    DO_INSTALL=1
else
    echo "python37-robotpy-cscore already installed"
fi
if [ "${DO_INSTALL}" == "0" ]; then
    echo "No packages to install."
else
    opkg install  ${PACKAGES[@]}
fi