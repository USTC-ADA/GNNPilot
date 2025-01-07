if [ $# -ne 1 ]; then
    echo "[Usage]: run.sh {input_matrix}"
    exit 1
fi
input_matrix=$1

cd test
python test_kernel.py $input_matrix