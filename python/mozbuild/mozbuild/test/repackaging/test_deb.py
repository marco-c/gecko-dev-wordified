#
This
Source
Code
Form
is
subject
to
the
terms
of
the
Mozilla
Public
#
License
v
.
2
.
0
.
If
a
copy
of
the
MPL
was
not
distributed
with
this
#
file
You
can
obtain
one
at
http
:
/
/
mozilla
.
org
/
MPL
/
2
.
0
/
.
import
os
from
contextlib
import
nullcontext
as
does_not_raise
from
unittest
.
mock
import
MagicMock
call
import
mozpack
.
path
as
mozpath
import
mozunit
import
pytest
from
mozbuild
.
repackaging
import
deb
def
test_copy_plain_deb_config
(
monkeypatch
)
:
    
def
mock_listdir
(
dir
)
:
        
assert
dir
=
=
"
/
template_dir
"
        
return
[
            
"
/
template_dir
/
debian_file1
.
in
"
            
"
/
template_dir
/
debian_file2
.
in
"
            
"
/
template_dir
/
debian_file3
"
            
"
/
template_dir
/
debian_file4
"
        
]
    
monkeypatch
.
setattr
(
deb
.
os
"
listdir
"
mock_listdir
)
    
def
mock_makedirs
(
dir
exist_ok
)
:
        
assert
dir
=
=
"
/
source_dir
/
debian
"
        
assert
exist_ok
is
True
    
monkeypatch
.
setattr
(
deb
.
os
"
makedirs
"
mock_makedirs
)
    
mock_copy
=
MagicMock
(
)
    
monkeypatch
.
setattr
(
deb
.
shutil
"
copy
"
mock_copy
)
    
deb
.
_copy_plain_deb_config
(
"
/
template_dir
"
"
/
source_dir
"
)
    
assert
mock_copy
.
call_args_list
=
=
[
        
call
(
"
/
template_dir
/
debian_file3
"
"
/
source_dir
/
debian
/
debian_file3
"
)
        
call
(
"
/
template_dir
/
debian_file4
"
"
/
source_dir
/
debian
/
debian_file4
"
)
    
]
def
test_inject_deb_distribution_folder
(
monkeypatch
)
:
    
def
mock_check_call
(
command
)
:
        
global
clone_dir
        
clone_dir
=
command
[
-
1
]
        
os
.
makedirs
(
os
.
path
.
join
(
clone_dir
"
desktop
/
deb
/
distribution
"
)
)
    
monkeypatch
.
setattr
(
deb
.
subprocess
"
check_call
"
mock_check_call
)
    
def
mock_copytree
(
source_tree
destination_tree
)
:
        
global
clone_dir
        
assert
source_tree
=
=
mozpath
.
join
(
clone_dir
"
desktop
/
deb
/
distribution
"
)
        
assert
destination_tree
=
=
"
/
source_dir
/
firefox
/
distribution
"
    
monkeypatch
.
setattr
(
deb
.
shutil
"
copytree
"
mock_copytree
)
    
deb
.
_inject_deb_distribution_folder
(
"
/
source_dir
"
"
Firefox
"
)
pytest
.
mark
.
parametrize
(
    
"
does_path_exits
expectation
"
    
(
        
(
True
does_not_raise
(
)
)
        
(
False
pytest
.
raises
(
deb
.
NoDebPackageFound
)
)
    
)
)
def
test_generate_deb_archive
(
    
monkeypatch
    
does_path_exits
    
expectation
)
:
    
monkeypatch
.
setattr
(
deb
"
_get_command
"
lambda
_
:
[
"
mock_command
"
]
)
    
monkeypatch
.
setattr
(
deb
.
subprocess
"
check_call
"
lambda
*
_
*
*
__
:
None
)
    
def
mock_exists
(
path
)
:
        
assert
path
=
=
"
/
target_dir
/
firefox_111
.
0_amd64
.
deb
"
        
return
does_path_exits
    
monkeypatch
.
setattr
(
deb
.
os
.
path
"
exists
"
mock_exists
)
    
def
mock_move
(
source_path
destination_path
)
:
        
assert
source_path
=
=
"
/
target_dir
/
firefox_111
.
0_amd64
.
deb
"
        
assert
destination_path
=
=
"
/
output
/
target
.
deb
"
    
monkeypatch
.
setattr
(
deb
.
shutil
"
move
"
mock_move
)
    
with
expectation
:
        
deb
.
_generate_deb_archive
(
            
source_dir
=
"
/
source_dir
"
            
target_dir
=
"
/
target_dir
"
            
output_file_path
=
"
/
output
/
target
.
deb
"
            
build_variables
=
{
                
"
DEB_PKG_NAME
"
:
"
firefox
"
                
"
DEB_PKG_VERSION
"
:
"
111
.
0
"
            
}
            
arch
=
"
x86_64
"
        
)
pytest
.
mark
.
parametrize
(
    
"
arch
is_chroot_available
expected
"
    
(
        
(
            
"
x86
"
            
True
            
[
                
"
chroot
"
                
"
/
srv
/
jessie
-
i386
"
                
"
bash
"
                
"
-
c
"
                
"
cd
/
tmp
/
*
/
source
;
dpkg
-
buildpackage
-
us
-
uc
-
b
-
-
host
-
arch
=
i386
"
            
]
        
)
        
(
"
x86
"
False
[
"
dpkg
-
buildpackage
"
"
-
us
"
"
-
uc
"
"
-
b
"
"
-
-
host
-
arch
=
i386
"
]
)
        
(
            
"
x86_64
"
            
True
            
[
                
"
chroot
"
                
"
/
srv
/
jessie
-
amd64
"
                
"
bash
"
                
"
-
c
"
                
"
cd
/
tmp
/
*
/
source
;
dpkg
-
buildpackage
-
us
-
uc
-
b
-
-
host
-
arch
=
amd64
"
            
]
        
)
        
(
            
"
x86_64
"
            
False
            
[
"
dpkg
-
buildpackage
"
"
-
us
"
"
-
uc
"
"
-
b
"
"
-
-
host
-
arch
=
amd64
"
]
        
)
    
)
)
def
test_get_command
(
monkeypatch
arch
is_chroot_available
expected
)
:
    
monkeypatch
.
setattr
(
deb
"
_is_chroot_available
"
lambda
_
:
is_chroot_available
)
    
assert
deb
.
_get_command
(
arch
)
=
=
expected
pytest
.
mark
.
parametrize
(
    
"
arch
does_dir_exist
expected_path
expected_result
"
    
(
        
(
"
x86
"
False
"
/
srv
/
jessie
-
i386
"
False
)
        
(
"
x86_64
"
False
"
/
srv
/
jessie
-
amd64
"
False
)
        
(
"
x86
"
True
"
/
srv
/
jessie
-
i386
"
True
)
        
(
"
x86_64
"
True
"
/
srv
/
jessie
-
amd64
"
True
)
    
)
)
def
test_is_chroot_available
(
    
monkeypatch
arch
does_dir_exist
expected_path
expected_result
)
:
    
def
_mock_is_dir
(
path
)
:
        
assert
path
=
=
expected_path
        
return
does_dir_exist
    
monkeypatch
.
setattr
(
deb
.
os
.
path
"
isdir
"
_mock_is_dir
)
    
assert
deb
.
_is_chroot_available
(
arch
)
=
=
expected_result
if
__name__
=
=
"
__main__
"
:
    
mozunit
.
main
(
)
