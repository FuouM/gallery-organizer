from util import dump_file_paths, dump_file_paths_ext_cond

test_folder = "public_test/"

# dump_file_paths(test_folder, "public_path_dump.txt")
dump_file_paths_ext_cond("test/raw/", "private_animated_dump.txt", ["gif", "webm", "mp4", "mov"])