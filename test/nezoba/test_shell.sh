#! /usr/bin/env bash

SCRIPT_1=$(cat <<EOF
# all help commands
help
help map
help show
help new
help delete
help copy
help edit
help save
help undo
help quit
#
# commands that don't work until a mapping is selected
show
delete
copy
edit
undo
#
# commands that require an argument
map
new
#
# create new mappings
new NS
map 0
show
new PC
map 1
show
#
# save the mappings to file
save
# 
# delete the mappings
map 0
delete
map 0
delete
#
# exit (doesn't ask for confirmation since nothing was changed before delete)
quit
EOF
)

SCRIPT_2=$(cat <<EOF
# reload saved mappings
map 0
# incorrect usage of edit
edit
edit another_attribute
edit 45
# incorrect presses
edit 1
K
edit 1
K_NON_EXISTING_BUTTON
edit 1
BUTTON_A
show
# correct usage of edit
edit title
SMM2 remix
edit description
This is just a test
of changing the description.

edit 3
K_A & B'
edit 3
A & B'
edit 1
# 'A & ' is interpreted as 'A & K_NOOP', which is equivalent to 'A'
A & 
show
#
# copy the mappings
copy
map 2
save
# do an edit, and then undo it
edit 3
K_DP_DOWN
show
undo
show
#
# exit (doesn't ask for confirmation since the latest changes were undone)
quit
EOF
)

# Reserve a temporary filename for the mappings
yaml_file=$(mktemp -u)

echo "$SCRIPT_1" | grep -v '^#' | nezoba cli "$yaml_file"
echo "$SCRIPT_2" | grep -v '^#' | nezoba cli "$yaml_file"

# Clean up the temporary file when done
rm "$yaml_file"
