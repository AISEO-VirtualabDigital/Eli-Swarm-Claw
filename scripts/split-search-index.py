import json, os, math

INDEX_PATH = '/home/z/my-project/data/eli-vault/03-Index/search-index.json'
INDEX_DIR = '/home/z/my-project/data/eli-vault/03-Index'
CHUNK_SIZE = 5000  # terms per file

with open(INDEX_PATH) as f:
    data = json.load(f)

terms = data['terms']
print(f'Total terms: {len(terms)}')

# Sort terms by number of files (most useful first)
sorted_terms = sorted(terms.items(), key=lambda x: len(x[1]), reverse=True)

chunks = math.ceil(len(sorted_terms) / CHUNK_SIZE)
print(f'Splitting into {chunks} files of {CHUNK_SIZE} terms')

for i in range(chunks):
    chunk = dict(sorted_terms[i*CHUNK_SIZE:(i+1)*CHUNK_SIZE])
    out = {
        'terms': chunk,
        '_meta': {'part': i+1, 'total': chunks, 'totalTerms': len(terms)},
    }
    path = os.path.join(INDEX_DIR, f'search-index-{i+1:02d}.json')
    with open(path, 'w') as f:
        json.dump(out, f)
    size = os.path.getsize(path) / 1024
    print(f'  Part {i+1}: {len(chunk)} terms, {size:.0f} KB')

# Remove original large file
os.remove(INDEX_PATH)
print(f'\nDone. {chunks} parts created. Original removed.')