#
!
/
usr
/
bin
/
python
#
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
'
'
'
This
script
analyzes
a
JSON
file
emitted
by
DMD
.
'
'
'
from
__future__
import
print_function
division
import
argparse
import
collections
import
json
import
re
import
sys
#
The
DMD
output
version
this
script
handles
.
outputVersion
=
1
#
If
-
-
ignore
-
alloc
-
fns
is
specified
stack
frames
containing
functions
that
#
match
these
strings
will
be
removed
.
allocatorFns
=
[
    
'
replace_malloc
'
    
'
replace_calloc
'
    
'
replace_realloc
'
    
'
replace_memalign
'
    
'
replace_posix_memalign
'
    
'
moz_xmalloc
'
    
'
moz_xcalloc
'
    
'
moz_xrealloc
'
    
'
operator
new
(
'
    
'
operator
new
[
]
(
'
    
'
g_malloc
'
    
'
g_slice_alloc
'
    
'
callocCanGC
'
    
'
reallocCanGC
'
    
'
vpx_malloc
'
    
'
vpx_calloc
'
    
'
vpx_realloc
'
    
'
vpx_memalign
'
    
'
js_malloc
'
    
'
js_calloc
'
    
'
js_realloc
'
    
'
pod_malloc
'
    
'
pod_calloc
'
    
'
pod_realloc
'
]
class
Record
(
object
)
:
    
def
__init__
(
self
)
:
        
self
.
numBlocks
=
0
        
self
.
reqSize
=
0
        
self
.
slopSize
=
0
        
self
.
usableSize
=
0
        
self
.
isSampled
=
False
        
self
.
usableSizes
=
collections
.
defaultdict
(
int
)
    
staticmethod
    
def
cmpByIsSampled
(
r1
r2
)
:
        
#
Treat
sampled
as
smaller
than
non
-
sampled
.
        
return
cmp
(
r2
.
isSampled
r1
.
isSampled
)
    
staticmethod
    
def
cmpByUsableSize
(
r1
r2
)
:
        
#
Sort
by
usable
size
then
req
size
then
by
isSampled
.
        
return
cmp
(
r1
.
usableSize
r2
.
usableSize
)
or
Record
.
cmpByReqSize
(
r1
r2
)
    
staticmethod
    
def
cmpByReqSize
(
r1
r2
)
:
        
#
Sort
by
req
size
then
by
isSampled
.
        
return
cmp
(
r1
.
reqSize
r2
.
reqSize
)
or
Record
.
cmpByIsSampled
(
r1
r2
)
    
staticmethod
    
def
cmpBySlopSize
(
r1
r2
)
:
        
#
Sort
by
slop
size
then
by
isSampled
.
        
return
cmp
(
r1
.
slopSize
r2
.
slopSize
)
or
Record
.
cmpByIsSampled
(
r1
r2
)
sortByChoices
=
{
    
'
usable
'
:
Record
.
cmpByUsableSize
#
the
default
    
'
req
'
:
Record
.
cmpByReqSize
    
'
slop
'
:
Record
.
cmpBySlopSize
}
def
parseCommandLine
(
)
:
    
#
24
is
the
maximum
number
of
frames
that
DMD
will
produce
.
    
def
range_1_24
(
string
)
:
        
value
=
int
(
string
)
        
if
value
<
1
or
value
>
24
:
            
msg
=
'
{
:
s
}
is
not
in
the
range
1
.
.
24
'
.
format
(
string
)
            
raise
argparse
.
ArgumentTypeError
(
msg
)
        
return
value
    
description
=
'
'
'
Analyze
heap
data
produced
by
DMD
.
If
no
files
are
specified
read
from
stdin
.
Write
to
stdout
unless
-
o
/
-
-
output
is
specified
.
'
'
'
    
p
=
argparse
.
ArgumentParser
(
description
=
description
)
    
p
.
add_argument
(
'
-
o
'
'
-
-
output
'
type
=
argparse
.
FileType
(
'
w
'
)
                   
help
=
'
output
file
;
stdout
if
unspecified
'
)
    
p
.
add_argument
(
'
-
f
'
'
-
-
max
-
frames
'
type
=
range_1_24
                   
help
=
'
maximum
number
of
frames
to
consider
in
each
trace
'
)
    
p
.
add_argument
(
'
-
r
'
'
-
-
ignore
-
reports
'
action
=
'
store_true
'
                   
help
=
'
ignore
memory
reports
data
;
useful
if
you
just
'
+
                        
'
want
basic
heap
profiling
'
)
    
p
.
add_argument
(
'
-
s
'
'
-
-
sort
-
by
'
choices
=
sortByChoices
.
keys
(
)
                   
default
=
sortByChoices
.
keys
(
)
[
0
]
                   
help
=
'
sort
the
records
by
a
particular
metric
'
)
    
p
.
add_argument
(
'
-
a
'
'
-
-
ignore
-
alloc
-
fns
'
action
=
'
store_true
'
                   
help
=
'
ignore
allocation
functions
at
the
start
of
traces
'
)
    
p
.
add_argument
(
'
-
b
'
'
-
-
show
-
all
-
block
-
sizes
'
action
=
'
store_true
'
                   
help
=
'
show
individual
block
sizes
for
each
record
'
)
    
p
.
add_argument
(
'
input_file
'
type
=
argparse
.
FileType
(
'
r
'
)
)
    
return
p
.
parse_args
(
sys
.
argv
[
1
:
]
)
def
main
(
)
:
    
args
=
parseCommandLine
(
)
    
j
=
json
.
load
(
args
.
input_file
)
    
if
j
[
'
version
'
]
!
=
outputVersion
:
        
raise
Exception
(
"
'
version
'
property
isn
'
t
'
{
:
d
}
'
"
.
format
(
outputVersion
)
)
    
#
Extract
the
main
parts
of
the
JSON
object
.
    
invocation
=
j
[
'
invocation
'
]
    
dmdEnvVar
=
invocation
[
'
dmdEnvVar
'
]
    
sampleBelowSize
=
invocation
[
'
sampleBelowSize
'
]
    
blockList
=
j
[
'
blockList
'
]
    
traceTable
=
j
[
'
traceTable
'
]
    
frameTable
=
j
[
'
frameTable
'
]
    
heapIsSampled
=
sampleBelowSize
>
1
#
is
sampling
present
?
    
#
Remove
allocation
functions
at
the
start
of
traces
.
    
if
args
.
ignore_alloc_fns
:
        
#
Build
a
regexp
that
matches
every
function
in
allocatorFns
.
        
escapedAllocatorFns
=
map
(
re
.
escape
allocatorFns
)
        
fn_re
=
re
.
compile
(
'
|
'
.
join
(
escapedAllocatorFns
)
)
        
#
Remove
allocator
fns
from
each
stack
trace
.
        
for
traceKey
frameKeys
in
traceTable
.
items
(
)
:
            
numSkippedFrames
=
0
            
for
frameKey
in
frameKeys
:
                
frameDesc
=
frameTable
[
frameKey
]
                
if
re
.
search
(
fn_re
frameDesc
)
:
                    
numSkippedFrames
+
=
1
                
else
:
                    
break
            
if
numSkippedFrames
>
0
:
                
traceTable
[
traceKey
]
=
frameKeys
[
numSkippedFrames
:
]
    
#
Trim
the
number
of
frames
.
    
for
traceKey
frameKeys
in
traceTable
.
items
(
)
:
        
if
len
(
frameKeys
)
>
args
.
max_frames
:
            
traceTable
[
traceKey
]
=
frameKeys
[
:
args
.
max_frames
]
    
#
Aggregate
blocks
into
records
.
All
sufficiently
similar
blocks
go
into
a
    
#
single
record
.
    
if
args
.
ignore_reports
:
        
liveRecords
=
collections
.
defaultdict
(
Record
)
    
else
:
        
unreportedRecords
=
collections
.
defaultdict
(
Record
)
        
onceReportedRecords
=
collections
.
defaultdict
(
Record
)
        
twiceReportedRecords
=
collections
.
defaultdict
(
Record
)
    
heapUsableSize
=
0
    
heapBlocks
=
0
    
for
block
in
blockList
:
        
#
For
each
block
we
compute
a
|
recordKey
|
and
all
blocks
with
the
same
        
#
|
recordKey
|
are
aggregated
into
a
single
record
.
The
|
recordKey
|
is
        
#
derived
from
the
block
'
s
'
alloc
'
and
'
reps
'
(
if
present
)
stack
        
#
traces
.
        
#
        
#
Each
stack
trace
has
a
key
in
the
JSON
file
.
But
we
don
'
t
use
that
        
#
key
to
construct
|
recordKey
|
;
instead
we
use
the
frame
keys
.
        
#
This
is
because
the
stack
trimming
done
for
-
-
max
-
frames
can
cause
        
#
stack
traces
with
distinct
trace
keys
to
end
up
with
the
same
frame
        
#
keys
and
these
should
be
considered
equivalent
.
E
.
g
.
if
we
have
        
#
distinct
traces
T1
:
[
A
B
C
]
and
T2
:
[
A
B
D
]
and
we
trim
the
final
frame
        
#
of
each
they
should
be
considered
equivalent
.
        
allocatedAt
=
block
[
'
alloc
'
]
        
if
args
.
ignore_reports
:
            
recordKey
=
str
(
traceTable
[
allocatedAt
]
)
            
records
=
liveRecords
        
else
:
            
recordKey
=
str
(
traceTable
[
allocatedAt
]
)
            
if
'
reps
'
in
block
:
                
reportedAts
=
block
[
'
reps
'
]
                
for
reportedAt
in
reportedAts
:
                    
recordKey
+
=
str
(
traceTable
[
reportedAt
]
)
                
if
len
(
reportedAts
)
=
=
1
:
                    
records
=
onceReportedRecords
                
else
:
                    
records
=
twiceReportedRecords
            
else
:
                
records
=
unreportedRecords
        
record
=
records
[
recordKey
]
        
if
'
req
'
in
block
:
            
#
not
sampled
            
reqSize
=
block
[
'
req
'
]
            
slopSize
=
block
.
get
(
'
slop
'
0
)
            
isSampled
=
False
        
else
:
            
#
sampled
            
reqSize
=
sampleBelowSize
            
if
'
slop
'
in
block
:
                
raise
Exception
(
"
'
slop
'
property
in
sampled
block
'
"
)
            
slopSize
=
0
            
isSampled
=
True
        
usableSize
=
reqSize
+
slopSize
        
heapUsableSize
+
=
usableSize
        
heapBlocks
+
=
1
        
record
.
numBlocks
+
=
1
        
record
.
reqSize
+
=
reqSize
        
record
.
slopSize
+
=
slopSize
        
record
.
usableSize
+
=
usableSize
        
record
.
isSampled
=
record
.
isSampled
or
isSampled
        
record
.
allocatedAt
=
block
[
'
alloc
'
]
        
if
args
.
ignore_reports
:
            
pass
        
else
:
            
if
'
reps
'
in
block
:
                
record
.
reportedAts
=
block
[
'
reps
'
]
        
record
.
usableSizes
[
(
usableSize
isSampled
)
]
+
=
1
    
#
Print
records
.
    
separator
=
'
#
'
+
'
-
'
*
65
+
'
\
n
'
    
def
number
(
n
isSampled
)
:
        
'
'
'
Format
a
number
with
comma
as
a
separator
and
a
'
~
'
prefix
if
it
'
s
        
sampled
.
'
'
'
        
return
'
{
:
}
{
:
d
}
'
.
format
(
'
~
'
if
isSampled
else
'
'
n
)
    
def
perc
(
m
n
)
:
        
return
0
if
n
=
=
0
else
(
100
*
m
/
n
)
    
def
plural
(
n
)
:
        
return
'
'
if
n
=
=
1
else
'
s
'
    
#
Prints
to
stdout
or
to
file
if
-
o
/
-
-
output
was
specified
.
    
def
out
(
*
arguments
*
*
kwargs
)
:
        
print
(
*
arguments
file
=
args
.
output
*
*
kwargs
)
    
def
printStack
(
traceTable
frameTable
traceKey
)
:
        
#
The
frame
number
is
always
'
#
00
'
(
see
DMD
.
h
for
why
)
so
we
have
to
        
#
replace
that
with
the
correct
frame
number
.
        
for
n
frameKey
in
enumerate
(
traceTable
[
traceKey
]
start
=
1
)
:
            
out
(
'
#
{
:
02d
}
{
:
}
'
.
format
(
n
frameTable
[
frameKey
]
[
3
:
]
)
)
    
def
printRecords
(
recordKind
records
heapUsableSize
)
:
        
RecordKind
=
recordKind
.
capitalize
(
)
        
out
(
separator
)
        
numRecords
=
len
(
records
)
        
cmpRecords
=
sortByChoices
[
args
.
sort_by
]
        
sortedRecords
=
sorted
(
records
.
values
(
)
cmp
=
cmpRecords
reverse
=
True
)
        
kindBlocks
=
0
        
kindUsableSize
=
0
        
maxRecord
=
1000
        
#
First
iteration
:
get
totals
etc
.
        
for
record
in
sortedRecords
:
            
kindBlocks
+
=
record
.
numBlocks
            
kindUsableSize
+
=
record
.
usableSize
        
#
Second
iteration
:
print
.
        
if
numRecords
=
=
0
:
            
out
(
'
#
no
{
:
}
heap
blocks
\
n
'
.
format
(
recordKind
)
)
        
kindCumulativeUsableSize
=
0
        
for
i
record
in
enumerate
(
sortedRecords
start
=
1
)
:
            
#
Stop
printing
at
the
|
maxRecord
|
th
record
.
            
if
i
=
=
maxRecord
:
                
out
(
'
#
{
:
}
:
stopping
after
{
:
d
}
heap
block
records
\
n
'
.
                    
format
(
RecordKind
i
)
)
                
break
            
kindCumulativeUsableSize
+
=
record
.
usableSize
            
isSampled
=
record
.
isSampled
            
out
(
RecordKind
+
'
{
'
)
            
out
(
'
{
:
}
block
{
:
}
in
heap
block
record
{
:
d
}
of
{
:
d
}
'
.
                
format
(
number
(
record
.
numBlocks
isSampled
)
                       
plural
(
record
.
numBlocks
)
i
numRecords
)
)
            
out
(
'
{
:
}
bytes
(
{
:
}
requested
/
{
:
}
slop
)
'
.
                
format
(
number
(
record
.
usableSize
isSampled
)
                       
number
(
record
.
reqSize
isSampled
)
                       
number
(
record
.
slopSize
isSampled
)
)
)
            
out
(
'
{
:
4
.
2f
}
%
of
the
heap
(
{
:
4
.
2f
}
%
cumulative
)
'
.
                
format
(
perc
(
record
.
usableSize
heapUsableSize
)
                       
perc
(
kindCumulativeUsableSize
heapUsableSize
)
)
)
            
if
args
.
ignore_reports
:
                
pass
            
else
:
                
out
(
'
{
:
4
.
2f
}
%
of
{
:
}
(
{
:
4
.
2f
}
%
cumulative
)
'
.
                    
format
(
perc
(
record
.
usableSize
kindUsableSize
)
                           
recordKind
                           
perc
(
kindCumulativeUsableSize
kindUsableSize
)
)
)
            
if
args
.
show_all_block_sizes
:
                
usableSizes
=
sorted
(
record
.
usableSizes
.
items
(
)
reverse
=
True
)
                
out
(
'
Individual
block
sizes
:
'
end
=
'
'
)
                
isFirst
=
True
                
for
(
usableSize
isSampled
)
count
in
usableSizes
:
                    
if
not
isFirst
:
                        
out
(
'
;
'
end
=
'
'
)
                    
out
(
'
{
:
}
'
.
format
(
number
(
usableSize
isSampled
)
)
end
=
'
'
)
                    
if
count
>
1
:
                        
out
(
'
x
{
:
d
}
'
.
format
(
count
)
end
=
'
'
)
                    
isFirst
=
False
                
out
(
)
            
out
(
'
Allocated
at
{
'
)
            
printStack
(
traceTable
frameTable
record
.
allocatedAt
)
            
out
(
'
}
'
)
            
if
args
.
ignore_reports
:
                
pass
            
else
:
                
if
hasattr
(
record
'
reportedAts
'
)
:
                    
for
n
reportedAt
in
enumerate
(
record
.
reportedAts
)
:
                        
again
=
'
again
'
if
n
>
0
else
'
'
                        
out
(
'
Reported
{
:
}
at
{
{
'
.
format
(
again
)
)
                        
printStack
(
traceTable
frameTable
reportedAt
)
                        
out
(
'
}
'
)
            
out
(
'
}
\
n
'
)
        
return
(
kindUsableSize
kindBlocks
)
    
#
Print
header
.
    
out
(
separator
)
    
out
(
'
Invocation
{
'
)
    
out
(
'
DMD
=
\
'
'
+
dmdEnvVar
+
'
\
'
'
)
    
out
(
'
Sample
-
below
size
=
'
+
str
(
sampleBelowSize
)
)
    
out
(
'
}
\
n
'
)
    
#
Print
records
.
    
if
args
.
ignore_reports
:
        
liveUsableSize
liveBlocks
=
\
            
printRecords
(
'
live
'
liveRecords
heapUsableSize
)
    
else
:
        
twiceReportedUsableSize
twiceReportedBlocks
=
\
            
printRecords
(
'
twice
-
reported
'
twiceReportedRecords
heapUsableSize
)
        
unreportedUsableSize
unreportedBlocks
=
\
            
printRecords
(
'
unreported
'
unreportedRecords
heapUsableSize
)
        
onceReportedUsableSize
onceReportedBlocks
=
\
            
printRecords
(
'
once
-
reported
'
onceReportedRecords
heapUsableSize
)
    
#
Print
summary
.
    
out
(
separator
)
    
out
(
'
Summary
{
'
)
    
if
args
.
ignore_reports
:
        
out
(
'
Total
:
{
:
}
bytes
in
{
:
}
blocks
'
.
            
format
(
number
(
liveUsableSize
heapIsSampled
)
                   
number
(
liveBlocks
heapIsSampled
)
)
)
    
else
:
        
fmt
=
'
{
:
15
}
{
:
>
12
}
bytes
(
{
:
6
.
2f
}
%
)
in
{
:
>
7
}
blocks
(
{
:
6
.
2f
}
%
)
'
        
out
(
fmt
.
            
format
(
'
Total
:
'
                   
number
(
heapUsableSize
heapIsSampled
)
                   
100
                   
number
(
heapBlocks
heapIsSampled
)
                   
100
)
)
        
out
(
fmt
.
            
format
(
'
Unreported
:
'
                   
number
(
unreportedUsableSize
heapIsSampled
)
                   
perc
(
unreportedUsableSize
heapUsableSize
)
                   
number
(
unreportedBlocks
heapIsSampled
)
                   
perc
(
unreportedBlocks
heapBlocks
)
)
)
        
out
(
fmt
.
            
format
(
'
Once
-
reported
:
'
                   
number
(
onceReportedUsableSize
heapIsSampled
)
                   
perc
(
onceReportedUsableSize
heapUsableSize
)
                   
number
(
onceReportedBlocks
heapIsSampled
)
                   
perc
(
onceReportedBlocks
heapBlocks
)
)
)
        
out
(
fmt
.
            
format
(
'
Twice
-
reported
:
'
                   
number
(
twiceReportedUsableSize
heapIsSampled
)
                   
perc
(
twiceReportedUsableSize
heapUsableSize
)
                   
number
(
twiceReportedBlocks
heapIsSampled
)
                   
perc
(
twiceReportedBlocks
heapBlocks
)
)
)
    
out
(
'
}
\
n
'
)
if
__name__
=
=
'
__main__
'
:
    
main
(
)
