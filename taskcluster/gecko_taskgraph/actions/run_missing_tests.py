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
logging
from
taskgraph
.
util
.
taskcluster
import
get_artifact
from
.
registry
import
register_callback_action
from
.
util
import
create_tasks
fetch_graph_and_labels
logger
=
logging
.
getLogger
(
__name__
)
register_callback_action
(
    
name
=
"
run
-
missing
-
tests
"
    
title
=
"
Run
Missing
Tests
"
    
symbol
=
"
rmt
"
    
description
=
(
        
"
Run
tests
in
the
selected
push
that
were
optimized
away
usually
by
SETA
.
"
        
"
\
n
"
        
"
This
action
is
for
use
on
pushes
that
will
be
merged
into
another
branch
"
        
"
to
check
that
optimization
hasn
'
t
hidden
any
failures
.
"
    
)
    
order
=
250
    
context
=
[
]
#
Applies
to
decision
task
)
def
run_missing_tests
(
parameters
graph_config
input
task_group_id
task_id
)
:
    
decision_task_id
full_task_graph
label_to_taskid
_
=
fetch_graph_and_labels
(
        
parameters
graph_config
    
)
    
parameters_writable
=
dict
(
parameters
)
    
parameters_writable
[
"
backstop
"
]
=
True
    
target_tasks
=
get_artifact
(
decision_task_id
"
public
/
target
-
tasks
.
json
"
)
    
#
Schedule
all
tasks
of
the
test
kind
even
if
they
had
been
already
    
#
scheduled
before
because
this
time
they
can
contain
more
and
different
    
#
test
manifests
which
earlier
did
not
appear
in
the
final
task
-
graph
-
-
    
#
those
were
the
optimized
tasks
.
    
to_run
=
[
]
    
for
label
in
target_tasks
:
        
task
=
full_task_graph
.
tasks
[
label
]
        
if
task
.
kind
!
=
"
test
"
:
            
continue
#
not
a
test
        
to_run
.
append
(
label
)
    
create_tasks
(
        
graph_config
        
to_run
        
full_task_graph
        
label_to_taskid
        
parameters
        
decision_task_id
        
"
all
"
    
)
    
logger
.
info
(
        
f
"
The
action
created
{
len
(
to_run
)
}
test
tasks
"
    
)
