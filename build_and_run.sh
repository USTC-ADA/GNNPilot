if [ $# -ne 1 ]; then
    echo "[Usage]: kg_run.sh {input_matrix}"
    exit 1
fi
input_matrix=$1

rm -rf build
mkdir build
cd build
cmake -DCMAKE_PREFIX_PATH="/root/anaconda3/envs/gnnadvisor/lib/python3.6/site-packages/torch/" ..
make -j 4

cd ../test
python test_kernel.py $input_matrix