#!/bin/bash
NAME="emf"
VERSION=2.5.0
TAG="R200906151043"

echo "Exporting from CVS..."
mkdir $NAME-$VERSION
pushd $NAME-$VERSION >/dev/null

MAPFILE=$NAME.map
TEMPMAPFILE=temp.map
wget "http://download.eclipse.org/modeling/emf/emf/downloads/drops/$VERSION/$TAG/directory.txt" -O $MAPFILE
dos2unix $MAPFILE
grep ^[a-z] $MAPFILE > $TEMPMAPFILE

gawk 'BEGIN {
	FS=","
}
{
if (NF <  4) {

	split($1, version, "=");
	split(version[1], directory, "@");
	cvsdir=split($2, dirName, ":");
	printf("cvs -d %s%s %s %s %s %s %s\n", ":pserver:anonymous@dev.eclipse.org:", dirName[cvsdir], "-q export -r", version[2], "-d", directory[2], directory[2]) | "/bin/bash";
}
else {

	split($1, version, "=");
	total=split($4, directory, "/");
	cvsdir=split($2, dirName, ":");
	printf("cvs -d %s%s %s %s %s %s %s\n", ":pserver:anonymous@dev.eclipse.org:", dirName[cvsdir], "-q export -r", version[2], "-d", directory[total], $4) | "/bin/bash";
}

}' $TEMPMAPFILE

rm $TEMPMAPFILE $MAPFILE
popd >/dev/null

echo "Creating tarball '$NAME-$VERSION.tar.gz'..."
tar -czf $NAME-$VERSION.tar.gz $NAME-$VERSION
