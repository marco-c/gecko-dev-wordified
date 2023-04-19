#
!
/
usr
/
bin
/
env
python3
import
glob
import
json
import
sys
#
Import
buildconfig
if
available
otherwise
set
has_buildconfig
to
False
so
#
we
skip
the
check
which
relies
on
it
.
try
:
    
import
buildconfig
except
ImportError
:
    
has_buildconfig
=
False
else
:
    
has_buildconfig
=
True
def
generate
(
output
*
input_paths
)
:
    
"
"
"
    
This
file
generates
a
ThirdPartyPaths
.
cpp
file
from
the
ThirdPartyPaths
.
txt
    
file
in
/
tools
/
rewriting
which
is
used
by
the
Clang
Plugin
to
help
identify
    
sources
which
should
be
ignored
.
    
"
"
"
    
tpp_list
=
[
]
    
lines
=
set
(
)
    
path_found
=
True
    
for
path
in
input_paths
:
        
with
open
(
path
)
as
f
:
            
lines
.
update
(
f
.
readlines
(
)
)
    
for
line
in
lines
:
        
line
=
line
.
strip
(
)
        
if
line
.
endswith
(
"
/
"
)
:
            
line
=
line
[
:
-
1
]
        
if
has_buildconfig
:
            
#
Ignore
lines
starting
with
UNVALIDATED
            
#
These
should
only
be
coming
from
Unvalidated
.
txt
            
if
line
.
startswith
(
"
UNVALIDATED
"
)
:
                
line
=
line
[
13
:
]
            
elif
not
glob
.
glob
(
buildconfig
.
topsrcdir
+
"
/
"
+
line
)
:
                
path_found
=
False
        
if
path_found
:
            
tpp_list
.
append
(
line
)
        
else
:
            
print
(
                
"
Third
-
party
path
"
                
+
line
                
+
"
does
not
exist
.
Remove
it
from
Generated
.
txt
or
"
                
+
"
ThirdPartyPaths
.
txt
and
try
again
.
"
            
)
            
sys
.
exit
(
1
)
    
tpp_strings
=
"
\
n
"
.
join
(
[
json
.
dumps
(
tpp
)
for
tpp
in
sorted
(
tpp_list
)
]
)
    
output
.
write
(
        
"
"
"
\
/
*
THIS
FILE
IS
GENERATED
BY
ThirdPartyPaths
.
py
-
DO
NOT
EDIT
*
/
#
include
<
stdint
.
h
>
const
char
*
MOZ_THIRD_PARTY_PATHS
[
]
=
{
  
%
s
}
;
extern
const
uint32_t
MOZ_THIRD_PARTY_PATHS_COUNT
=
%
d
;
"
"
"
        
%
(
tpp_strings
len
(
tpp_list
)
)
    
)
