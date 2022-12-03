#!/bin/bash
[[ $1 =~ password: ]] && cat || SSH_ASKPASS="$0" DISPLAY=nothing:0 exec setsid "$@"
