%global major_ver 10
%global minor_ver 3
%global patch_ver 0

# Don't generate any debuginfo packages
%global debug_package %{nil}

# Post install checking of installed files is determined by three variables:
#
# __arch_install_post
# __os_install_post
# __spec_install_post
#
# each of which can be examined with rpm --eval %var. The last one
# is the catenation of the first two.
#
# At the least we want to disable rpath checking with
#
# define __arch_install_post /usr/lib/rpm/check-buildroot
#
# which keeps the check for occurences of $RPM_BUILD_ROOT in scripts -
# useful to do this sometimes, but very time consuming
#
%define __arch_install_post /usr/lib/rpm/check-buildroot
%define __os_install_post %{nil}

# Disable automatic dependency and provides information
%define __find_provides %{nil} 
%define __find_requires %{nil} 
%define _use_internal_dependency_generator 0
Autoprov: 0
Autoreq: 0


Name:		Mathematica
Version:	%{major_ver}.%{minor_ver}.%{patch_ver}
Release:	3%{?dist}
Summary:	A platform for scientific, engineering, and mathematical computation

Group:		Applications/Engineering
License:	Proprietary
URL:		http://www.wolfram.com
Source0:	Mathematica_%{version}_LINUX.sh
NoSource:       0

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if 0%{?fedora} <= 22
BuildRequires:	prelink
%endif
BuildRequires:  hicolor-icon-theme
BuildRequires:  desktop-file-utils
BuildRequires:  symlinks

%description
Mathematica is a computational software program used in scientific,
engineering, and mathematical fields and other areas of technical
computing.

%prep
%setup -T -c %{name}-%{version}

cp %SOURCE0 .
chmod +x Mathematica_%{version}_LINUX.sh

%build
# Nothing to do

%install
%define destdir /opt/%{name}/%{version}

#define __spec_install_pre /bin/true
./Mathematica_%{version}_LINUX.sh -- \
	-auto -createdir=y -selinux=y -verbose \
	-targetdir=$RPM_BUILD_ROOT%{destdir} \
 	-execdir=$RPM_BUILD_ROOT%{destdir}/bin

# Fix up prelink error 
# prelink: # /home/jgu/rpmbuild/BUILDROOT/Mathematica-8.0.1-1.el6.x86_64/opt/Mathematica/8.0.1/SystemFiles/Libraries/Linux/libPHANToMIO.so.4:
# Could not find one of the dependencies)
# See eg. http://www.redhat.com/archives/rpm-list/2008-May/msg00011.html
%if %{major_ver} == 9 && 0%{?fedora} <= 22
prelink -u $RPM_BUILD_ROOT%{destdir}/SystemFiles/Libraries/Linux/libPHANToMIO.so.4
%endif

# Fix up hardcoded references to the buildroot in installed files -
# this silences the check-buildroot script that is ran by rpmbuild
# after %%install
for i in $RPM_BUILD_ROOT%{destdir}/SystemFiles/Installation/*.desktop ; do
    sed -i -e "s|$RPM_BUILD_ROOT||g" $i
done

# Install menu and mimetype information
install -d $RPM_BUILD_ROOT%{_datadir}/applications
install -d $RPM_BUILD_ROOT%{_datadir}/mime/packages

pushd $RPM_BUILD_ROOT%{destdir}/SystemFiles/Installation

# The wolfram-mathematica8.desktop file has strange leading and
# trailing white space, so fix this, and also add a trailing semicolon
# to the MimeType entry to prevent desktop-file-validate from failing
# Note: wolfram-mathematica.desktop (without the 8) doesn't have the
# correct path for Exec etc
sed -i -e 's/^[ \t]*//;s/[ \t]*$//' wolfram-mathematica%{major_ver}.desktop 
sed -i -e '/MimeType/ s/$/;/' wolfram-mathematica%{major_ver}.desktop

# Unfortunately the freedesktop.org.xml contains mime entries for
# mathematica notebook files which set the application type to
# application/mathematica with an alias to
# /application/x-mathematica. This overrides the wolfram shipped mime
# file for notebook files. As a fix, we'll add the
# application/mathematica and application/x-mathematica mime types to
# the desktop file. See:
#
# https://bugs.freedesktop.org/show_bug.cgi?id=93811
# https://bugzilla.redhat.com/show_bug.cgi?id=1300723
#
# We'll also add the Development category rather than creating a
# sub-menu just for mathematica
desktop-file-install wolfram-mathematica%{major_ver}.desktop \
                     --add-mime-type=application/mathematica \
                     --add-mime-type=application/x-mathematica \
                     --add-category=Development \
                     --dir=$RPM_BUILD_ROOT%{_datadir}/applications

# Fix the vnd.wolfram.nb.xml file - increase the weight of the glob to
# 80, and add magic entries for vnd.wolfram.mathematica and
# application/mathematica
cat > application-vnd.wolfram.nb.xml <<EOF
<?xml version="1.0"?>
<mime-info xmlns='http://www.freedesktop.org/standards/shared-mime-info'>
  <mime-type type="application/vnd.wolfram.nb">
    <comment>Wolfram Notebook</comment>
    <magic priority="80">
      <match type="string" offset="0:100" value="vnd.wolfram.nb" />
      <match type="string" offset="0:100" value="vnd.wolfram.mathematica" />
      <match type="string" offset="0:100" value="application/mathematica" />
    </magic>
    <generic-icon name="application-mathematica" />
    <glob pattern="*.nb" weight="80"/>
  </mime-type>
</mime-info>
EOF


# Install mime files
cp -a *.xml $RPM_BUILD_ROOT%{_datadir}/mime/packages/

popd
 
# Install icons
install -d $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/{32x32,64x64,128x128}/{apps,mimetypes}
pushd $RPM_BUILD_ROOT%{destdir}/SystemFiles/FrontEnd/SystemResources/X
for i in "32" "64" "128"; do
    cp -a App.Mathematica.${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps/wolfram-mathematica.png
    cp -a App.Player.${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps/wolfram-mathematicaplayer.png

    for v in "cdf" "mathematica.package" "nb" "player" "wl" ; do
	cp -a vnd.wolfram.${v}.${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/mimetypes/application-vnd.wolfram.${v}.png
    done

    # We also need to have icons for the broken freedesktop mime types (see above). Sigh.
    pushd $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/mimetypes
    ln -s application-vnd.wolfram.${v}.png application-mathematica.png
    popd
done
popd

# Install man pages 
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
pushd $RPM_BUILD_ROOT%{destdir}/SystemFiles/SystemDocumentation/Unix
cp -a *.1 $RPM_BUILD_ROOT%{_mandir}/man1
popd

# Create mathpass file specifying license server 
cat > $RPM_BUILD_ROOT%{destdir}/Configuration/Licensing/mathpass << EOF
!mathlm-server.ucl.ac.uk
EOF

# Create file to add binaries to PATH
install -d $RPM_BUILD_ROOT%{_sysconfdir}/profile.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/mathematica%{major_ver}.sh << EOF
export PATH=\$PATH:%{destdir}/bin
EOF

# Create directories for Mathematica system wide package installation
# (corresponding to $BaseDirectory etc)
install -d $RPM_BUILD_ROOT%{_datadir}/Mathematica/{Applications,Autoload}

# Unfortunately the installer script creates absolute symlinks which
# break once files are moved out of the build root. So, we have to
# manually recreate them here as relative links
symlinks -r -c -v $RPM_BUILD_ROOT%{destdir}


%clean
rm -rf $RPM_BUILD_ROOT

%post
# Update icon cache with new icons
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

# Update mime database - needed because we install xml mime definitions
/usr/bin/update-mime-database %{_datadir}/mime &> /dev/null || :

# Update desktop database - needed because .desktop file has a Mimeinfo entry
/usr/bin/update-desktop-database &> /dev/null || :

%postun
# Update icon cache to reflect removed icons
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

# Update mime database - needed because we install xml mime definitions
/usr/bin/update-mime-database %{_datadir}/mime &> /dev/null || :

# Update desktop database - needed because .desktop file has a Mimeinfo entry
/usr/bin/update-desktop-database &> /dev/null || :

%posttrans
# Update icon cache to reflect removed icons
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

# Update mime-database here too
/usr/bin/update-mime-database %{?fedora:-n} %{_datadir}/mime &> /dev/null || :


%files
%defattr(-,root,root,-)
%{destdir}
%{_datadir}/Mathematica/Autoload
%{_datadir}/Mathematica/Applications
%{_sysconfdir}/profile.d/*
%{_datadir}/applications/*
%{_datadir}/icons/hicolor/128x128/apps/*
%{_datadir}/icons/hicolor/128x128/mimetypes/*
%{_datadir}/icons/hicolor/32x32/apps/*
%{_datadir}/icons/hicolor/32x32/mimetypes/*
%{_datadir}/icons/hicolor/64x64/apps/*
%{_datadir}/icons/hicolor/64x64/mimetypes/*
%{_datadir}/mime/packages/*
%{_mandir}/man1/*

%changelog
* Fri Mar  4 2016 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 10.3.0-3
- Fix up mime types properly

* Thu Jan 21 2016 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 10.3.0-2
- Add symlinks for icons for the broken freedesktop mime types

* Thu Jan 21 2016 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 10.3.0-1
- Update to 10.3.0
- Move to using nosrc
- Only BR require prelink on Fedora < 23
- Fix up desktop file to deal with the freedesktop.org defined mime types
- Clean ups
- Update mime database in %%posttrans as well as %%post

* Thu Oct  1 2015 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 10.2.0-1
- Update to 10.2.0

* Thu Feb 21 2013 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 9.0.1-1
- Update to 9.0.1
- Add /usr/share/Mathematica/{Applications,Autoload} directories to package
- Other cleanups

* Fri Feb 15 2013 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 9.0.0-1
- Update to 9.0.0

* Fri Apr 27 2012 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 8.0.4-3
- Fix up .desktop file to add an entry under Programming menu

* Fri Apr 27 2012 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 8.0.4-2
- Properly install icons, desktop entries, mimetypes and manpages
- Re-enable the check-buildroot script in __arch_install_post, but
  still disable rpath checking
- No longer set __spec_install_post to nil

* Fri Apr 27 2012 Jonathan G. Underwood <jonathan.underwood@gmail.com> - 8.0.4-1
- Update to 8.0.4

* Mon Jul 11 2011 Jonathan G. Underwood <jgu@burroughs.theory.phys.ucl.ac.uk> - 8.0.1-3
- Fix error with setting \$PATH in bash script

* Mon Jul 11 2011 Jonathan G. Underwood <jgu@burroughs.theory.phys.ucl.ac.uk> - 8.0.1-2
- Fix error with setting \$PATH in bash script

* Fri Jul  8 2011 Jonathan G. Underwood <jgu@burroughs.theory.phys.ucl.ac.uk> - 8.0.1-1
- Initial package

