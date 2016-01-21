rpm-mathematica
===============

RPM for Mathematica

Building the nosrc rpm using mock on Fedora
-------------------------------------------

1. Build a src rpm as usual

```shell
rpmbuild -bs Mathematica.spec 
```
2. Initialize a mock chroot

```shell
mock -r fedora-23-x86_64 init
```

3. Copy the Mathematica installer bundle into the chroot

```shell
mock -r fedora-23-x86_64 --copyin Mathematica_10.3.0_LINUX.sh /builddir/build/SOURCES/
```

4. Kick off the build without cleaning the chroot

```shell
mock -v --dnf -r fedora-23-x86_64 --no-clean --rebuild Mathematica-10.3.0-1.fc23.nosrc.rpm 
```
