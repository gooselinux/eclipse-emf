%if 0%{?rhel} >= 6
%global debug_package %{nil}
%endif

%global eclipse_base     %{_libdir}/eclipse
%global eclipse_dropin   %{_datadir}/eclipse/dropins

Name:      eclipse-emf
Version:   2.5.0
Release:   4.4%{?dist}
Summary:   Eclipse Modeling Framework (EMF) Eclipse plugin
Group:     System Environment/Libraries
License:   EPL
URL:       http://www.eclipse.org/modeling/emf/

# source tarball and the script used to generate it from upstream's source control
# script usage:
# $ sh get-emf.sh
Source0:   emf-%{version}.tar.gz
Source1:   get-emf.sh

# don't depend on ANT_HOME and JAVA_HOME environment vars
Patch0:    %{name}-make-homeless.patch
# look inside correct directory for platform docs
Patch1:    %{name}-platform-docs-location.patch
# look inside all symlink'd plugin directories when building javadocs
# this patch has been sent upstream, see eclipse.org bug #281779
Patch2:    %{name}-symlinked-classpath.patch
# don't include hidden files in source plugins
# (mostly to shut rpmlint up, but these files aren't needed for source plugin builds; they
# are still included such that the example installer can create full sample projects in 
# your workspace)
Patch3:    %{name}-build-props.patch
# bundle examples in example-installer plugins from source in tarball instead of from cvs
Patch4:    %{name}-bundle-examples.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if 0%{?rhel} >= 6
ExclusiveArch: i686 x86_64
%else
BuildArch: noarch
%endif

# we require 1.6.0 because the javadocs fail to build otherwise
BuildRequires:    java-devel >= 1:1.6.0
BuildRequires:    java-javadoc
BuildRequires:    jpackage-utils
BuildRequires:    eclipse-pde >= 1:3.5.0
BuildRequires:    dos2unix
Requires:         java
Requires:         jpackage-utils
Requires:         eclipse-platform >= 1:3.5.0

# the standalone package was deprecated and removed in EMF 2.3 (see eclipse.org bug #191837)
Obsoletes:        %{name}-standalone < 2.4

# the SDO sub-project was terminated upstream and removed in EMF 2.5 (see eclipse.org bug #251402)
Obsoletes:        %{name}-sdo < 2.5
Obsoletes:        %{name}-sdo-sdk < 2.5

%description
The Eclipse Modeling Framework (EMF) allows developers to build tools and
other applications based on a structured data model. From a model
specification described in XMI, EMF provides tools and runtime support to
produce a set of Java classes for the model, along with a set of adapter
classes that enable viewing and command-based editing of the model, and a
basic editor.

%package   sdk
Summary:   Eclipse EMF SDK
Group:     System Environment/Libraries
Requires:  java-javadoc
Requires:  eclipse-pde >= 1:3.5.0
Requires:  %{name} = %{version}-%{release}

%description sdk
Documentation and source for the Eclipse Modeling Framework (EMF).

%package   xsd
Summary:   XML Schema Definition (XSD) Eclipse plugin
Group:     System Environment/Libraries
Requires:  %{name} = %{version}-%{release}

%description xsd
The XML Schema Definition (XSD) plugin is a library that provides an API for
manipulating the components of an XML Schema as described by the W3C XML
Schema specifications, as well as an API for manipulating the DOM-accessible
representation of XML Schema as a series of XML documents.

%package   xsd-sdk
Summary:   Eclipse XSD SDK
Group:     System Environment/Libraries
Requires:  java-javadoc
Requires:  eclipse-pde >= 1:3.5.0
Requires:  %{name}-xsd = %{version}-%{release}
Requires:  %{name}-sdk = %{version}-%{release}

%description xsd-sdk
Documentation and source for the Eclipse XML Schema Definition (XSD) plugin.

%package   examples
Summary:   Eclipse EMF/XSD examples
Group:     System Environment/Libraries
Requires:  %{name}         = %{version}-%{release}
Requires:  %{name}-xsd     = %{version}-%{release}

%description examples
Installable versions of the example projects from the SDKs that demonstrate how
to use the Eclipse Modeling Framework (EMF) and XML Schema Definition (XSD)
plugins.

%prep
%setup -q -n emf-%{version}

%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p1
%patch4 -p1

rm org.eclipse.emf.doc/tutorials/jet2/jetc-task.jar
rm org.eclipse.emf.test.core/data/data.jar

# link to local java api javadocs
sed -i -e "s|http://java.sun.com/j2se/1.5/docs/api/|%{_javadocdir}/java|" -e "s|\${javaHome}/docs/api/|%{_javadocdir}/java|" \
  org.eclipse.emf.doc/build/javadoc.xml.template \
  org.eclipse.xsd.doc/build/javadoc.xml.template

# make sure upstream hasn't sneaked in any jars we don't know about
JARS=""
for j in `find -name "*.jar"`; do
  if [ ! -L $j ]; then
    JARS="$JARS $j"
  fi
done
if [ ! -z "$JARS" ]; then
   echo "These jars should be deleted and symlinked to system jars: $JARS"
   exit 1
fi

%build
# Note: We use forceContextQualifier because the docs plugins use custom build
#       scripts and don't work otherwise.
OPTIONS="-DjavacTarget=1.5 -DjavacSource=1.5 -DforceContextQualifier=v200906151043"

# We build the emf, xsd and examples features seperately, rather than just
# building the "all" feature, because it makes the files section easier to
# maintain (i.e. we don't have to know when upstream adds a new plugin)

# build emf features
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.emf -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.emf.sdk -a "$OPTIONS"

# build xsd features
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.xsd -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.xsd.edit -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.xsd.editor -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.xsd.mapping -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.xsd.mapping.editor -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.xsd.ecore.converter -a "$OPTIONS"
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.xsd.sdk -a "$OPTIONS"

# build examples features
%{eclipse_base}/buildscripts/pdebuild -f org.eclipse.emf.examples -a "$OPTIONS"

%install
rm -rf %{buildroot}
install -d -m 755 %{buildroot}%{eclipse_dropin}
unzip -q -n -d %{buildroot}%{eclipse_dropin}/emf          build/rpmBuild/org.eclipse.emf.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/emf-sdk      build/rpmBuild/org.eclipse.emf.sdk.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/xsd          build/rpmBuild/org.eclipse.xsd.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/xsd          build/rpmBuild/org.eclipse.xsd.edit.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/xsd          build/rpmBuild/org.eclipse.xsd.editor.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/xsd          build/rpmBuild/org.eclipse.xsd.mapping.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/xsd          build/rpmBuild/org.eclipse.xsd.mapping.editor.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/xsd          build/rpmBuild/org.eclipse.xsd.ecore.converter.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/xsd-sdk      build/rpmBuild/org.eclipse.xsd.sdk.zip
unzip -q -n -d %{buildroot}%{eclipse_dropin}/emf-examples build/rpmBuild/org.eclipse.emf.examples.zip

# the non-sdk builds are a subset of the sdk builds, so delete duplicate features & plugins from the sdks
(cd %{buildroot}%{eclipse_dropin}/emf-sdk/eclipse/features && ls %{buildroot}%{eclipse_dropin}/emf/eclipse/features | xargs rm -rf)
(cd %{buildroot}%{eclipse_dropin}/emf-sdk/eclipse/plugins  && ls %{buildroot}%{eclipse_dropin}/emf/eclipse/plugins  | xargs rm -rf)
(cd %{buildroot}%{eclipse_dropin}/xsd-sdk/eclipse/features && ls %{buildroot}%{eclipse_dropin}/xsd/eclipse/features | xargs rm -rf)
(cd %{buildroot}%{eclipse_dropin}/xsd-sdk/eclipse/plugins  && ls %{buildroot}%{eclipse_dropin}/xsd/eclipse/plugins  | xargs rm -rf)

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{eclipse_dropin}/emf
%doc org.eclipse.emf-feature/rootfiles/*

%files sdk
%defattr(-,root,root,-)
%{eclipse_dropin}/emf-sdk
%doc org.eclipse.emf.sdk-feature/rootfiles/*

%files xsd
%defattr(-,root,root,-)
%{eclipse_dropin}/xsd
%doc org.eclipse.xsd-feature/rootfiles/*

%files xsd-sdk
%defattr(-,root,root,-)
%{eclipse_dropin}/xsd-sdk
%doc org.eclipse.xsd.sdk-feature/rootfiles/*

%files examples
%defattr(-,root,root,-)
%{eclipse_dropin}/emf-examples
%doc org.eclipse.emf.examples-feature/rootfiles/*

%changelog
* Fri Feb 12 2010 Andrew Overholt <overholt@redhat.com> 2.5.0-4.4
- Don't build debuginfo if building arch-specific packages.

* Thu Jan 21 2010 Andrew Overholt <overholt@redhat.com> 2.5.0-4.3
- Make arch-specific (x86, x86_64).

* Mon Dec 14 2009 Andrew Overholt <overholt@redhat.com> 2.5.0-4.2
- Retain BuildArch: noarch.

* Tue Dec  1 2009 Dennis Gregorovic <dgregor@redhat.com> - 2.5.0-4.1
- Only build on x86 and x86_64 since we only have eclipse on those arches

* Sat Sep 19 2009 Mat Booth <fedora@matbooth.co.uk> - 2.5.0-4
- Re-enable jar repacking now that RHBZ #461854 has been resolved.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 02 2009 Mat Booth <fedora@matbooth.co.uk> 2.5.0-2
- SDK requires PDE for example plug-in projects.

* Sun Jun 28 2009 Mat Booth <fedora@matbooth.co.uk> 2.5.0-1
- Update to 2.5.0 final release (Galileo).
- Build the features seperately to allow for a saner %%files section.

* Fri May 22 2009 Alexander Kurtakov <akurtako@redhat.com> 2.5.0-0.2.RC1
- Update to 2.5.0 RC1.
- Use %%global instead of %%define. 

* Sat Apr 18 2009 Mat Booth <fedora@matbooth.co.uk> 2.5.0-0.1.M6
- Update to Milestone 6 release of 2.5.0.
- Require Eclipse 3.5.0.

* Tue Apr 7 2009 Alexander Kurtakov <akurtako@redhat.com> 2.4.2-3
- Fix directory ownership.

* Mon Mar 23 2009 Alexander Kurtakov <akurtako@redhat.com> 2.4.2-2
- Rebuild to not ship p2 context.xml.
- Remove context.xml from %%files section.

* Sat Feb 28 2009 Mat Booth <fedora@matbooth.co.uk> 2.4.2-1
- Update for Ganymede SR2.

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 03 2009 Mat Booth <fedora@matbooth.co.uk> 2.4.1-4
- Make context qualifier the same as upstream.

* Sat Jan 10 2009 Mat Booth <fedora@matbooth.co.uk> 2.4.1-3
- Removed AOT bits and change package names to what they used to be.
- Obsolete standalone package.

* Tue Dec 23 2008 Mat Booth <fedora@matbooth.co.uk> 2.4.1-2
- Build example installer plugins using the source from the tarball instead of
  trying to get the examples from source control a second time.

* Fri Dec 12 2008 Mat Booth <fedora@matbooth.co.uk> 2.4.1-1
- Initial release, based on eclipse-gef spec file, but with disabled AOT
  compiled bits because of RHBZ #477707.
