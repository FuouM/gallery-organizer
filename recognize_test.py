import pickle
from recognizer import danbooru_recognizer

test_folder = "public_test/"
test_files = [
    "1598649079544.jpg"
    ,"1630254672065.png"
    ,"1630200094228.jpg"
    ,"1630143860485.png"
    ,"1656276403586.jpg"
    ,"Fw-2uKyaUAAYzdb.jpg"
    ,"FxBb8csaAAsRcqm.jpg"
    ,"1603974269524.jpg"
    ,"1628224351865.jpg"
    ,"1640356122474.png"
    ,"2347329483241324132423.png"
    ]

test_gifs = [
    "1664081283396885.gif"
]

danbooru = danbooru_recognizer()
danbooru.load()
res = danbooru.inference_gpu([test_folder + y for y in test_files])
dump_pickle_path = 'public_test.pickle'
# for result, res_dict in res:
#     print(result, res_dict)
# danbooru.dump_pickle(res, dump_pickle_path)
    