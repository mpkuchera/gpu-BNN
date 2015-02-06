export HERE=`pwd`
if [ "$LD_LIBRARY_PATH" ]; then
    export LD_LIBRARY_PATH=$HERE/lib:$LD_LIBRARY_PATH
else
    export LD_LIBRARY_PATH=$HERE/lib
fi
export PATH=$HERE/bin:$PATH


