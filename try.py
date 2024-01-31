# def concertQueue(N,A):
    
#     #this is default OUTPUT. You can change it.
#     result = []
    
#     #write your Logic here:
#     next_person = 0
#     list_length = len(result)
#     for i in A:
#         if i < next_person:
#             result.append(i)
#         next_person = i


#     return result

# #INPUT [uncomment & modify if required]
# def raw_input():
#     return '5,4,3,2,1'

# N = int(raw_input())
# temp = raw_input().split()
# A = list(map(int,temp))

def process_large_list(data, chunk_size=100):
    total_items = len(data)
    for i in range(0, total_items, chunk_size):
        chunk = data[i:i + chunk_size]
        process_chunk(chunk)

def process_chunk(chunk):
    # Do something with the chunk of data
    for item in chunk:
        process_item(item)

def process_item(item):
    # Your processing logic for each item
    print(item)

# Example usage
large_data = range(2000)  # Replace this with your actual data
process_large_list(large_data)
