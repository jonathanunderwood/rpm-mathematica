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
#define __arch_install_post %{nil}
%define __arch_install_post /usr/lib/rpm/check-buildroot
%define __os_install_post %{nil}

# Disable automatic dependency and provides information
%define __find_provides %{nil} 
%define __find_requires %{nil} 
%define _use_internal_dependency_generator 0
Autoprov: 0
Autoreq: 0


Name:		Mathematica
Version:	9.0.1
Release:	1%{?dist}
Summary:	A platform for scientific, engineering, and mathematical computation

Group:		Applications/Engineering
License:	Proprietary
URL:		http://wwww.wolfram.com
Source0:	%{name}_%{version}_LINUX.sh
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	prelink
BuildRequires:  hicolor-icon-theme
BuildRequires:  desktop-file-utils

%description
Mathematica is a computational software program used in scientific,
engineering, and mathematical fields and other areas of technical
computing.

%prep
%setup -T -c %{name}-%{version}

cp %SOURCE0 .
chmod +x %{name}_%{version}_LINUX.sh

%build
# Nothing to do

%install
rm -rf $RPM_BUILD_ROOT

%define destdir /opt/%{name}/%{version}

./%{name}_%{version}_LINUX.sh -- \
	-auto -createdir=y -selinux=y -verbose \
	-targetdir=$RPM_BUILD_ROOT%{destdir} \
 	-execdir=$RPM_BUILD_ROOT%{destdir}/bin

# Unfortunately the installer script creates absolute symlinks which
# break once files are moved out of the build root. So, we have to
# manually recreate them here as relative links
before=($(echo $RPM_BUILD_ROOT%{destdir}/bin/*))

rm -rf $RPM_BUILD_ROOT%{destdir}/bin/*

for i in `ls $RPM_BUILD_ROOT%{destdir}/Executables` ; do
    ln -s %{destdir}/Executables/${i} $RPM_BUILD_ROOT%{destdir}/bin/${i}
done

ln -s %{destdir}/SystemFiles/Kernel/Binaries/Linux-x86-64/MathematicaScript $RPM_BUILD_ROOT%{destdir}/bin/MathematicaScript

after=($(echo $RPM_BUILD_ROOT%{destdir}/bin/*))

if [ "${before[*]}" != "${after[*]}" ] ; then
   echo "$RPM_BUILD_ROOT%{destdir}/bin doesn't contain all required symlinks after relinking"
   exit 1
fi

# Fix up prelink error 
# prelink: # /home/jgu/rpmbuild/BUILDROOT/Mathematica-8.0.1-1.el6.x86_64/opt/Mathematica/8.0.1/SystemFiles/Libraries/Linux/libPHANToMIO.so.4:
# Could not find one of the dependencies)
# See eg. http://www.redhat.com/archives/rpm-list/2008-May/msg00011.html
prelink -u $RPM_BUILD_ROOT%{destdir}/SystemFiles/Libraries/Linux/libPHANToMIO.so.4

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
sed -i -e 's/^[ \t]*//;s/[ \t]*$//' wolfram-mathematica9.desktop 
sed -i -e '/MimeType/ s/$/;/' wolfram-mathematica9.desktop 

# We don't want to create a separate sub-menu just for Mathematica, so
# we'll add it to the Programming sub-menu
cat >> wolfram-mathematica9.desktop <<EOF
Categories=Development;
EOF

cp -a wolfram-mathematica9.desktop $RPM_BUILD_ROOT%{_datadir}/applications/wolfram-mathematica9.desktop
desktop-file-validate $RPM_BUILD_ROOT%{_datadir}/applications/wolfram-mathematica9.desktop

cp -a *.xml $RPM_BUILD_ROOT%{_datadir}/mime/packages/
popd
 
# Install icons
install -d $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/{32x32,64x64,128x128}/{apps,mimetypes}
pushd $RPM_BUILD_ROOT%{destdir}/SystemFiles/FrontEnd/SystemResources/X
for i in "32" "64" "128"; do
    cp -a Mathematica-${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps/wolfram-mathematica.png
    cp -a MathematicaPlayer-${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps/wolfram-mathematicaplayer.png
    cp -a vnd.wolfram.cdf-${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/mimetypes/application-vnd.wolfram.cdf.png
 
    cp -a MathematicaDoc-${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/mimetypes/application-mathematica.png
    cp -a MathematicaPlayerDoc-${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/mimetypes/application-mathematicaplayer.png
    cp -a vnd.wolfram.cdfDoc-${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/mimetypes/application-vnd.wolfram.cdf.png
 
    cp -a MathematicaDoc-${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/mimetypes/gnome-mime-application-mathematica.png
    cp -a MathematicaPlayerDoc-${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/mimetypes/gnome-mime-application-mathematicaplayer.png
    cp -a vnd.wolfram.cdfDoc-${i}.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/mimetypes/gnome-mime-application-vnd.wolfram.cdf.png
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
cat > $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/mathematica.sh << EOF
export PATH=\$PATH:%{destdir}/bin
EOF

# Create directories for Mathematica system wide package installation
# (corresponding to $BaseDirectory etc)
install -d $RPM_BUILD_ROOT%{_datadir}/Mathematica/{Applications,Autoload}

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

