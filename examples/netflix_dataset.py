import os
import time # only for debugging

import yaupon

yaupon.config.graph_memory_usage = 'MEMORY_EXTERNAL'

def build_graph(path = "."):
    g = yaupon.Graph(database_name = 'movies.db3', use_vertex_cache = True)
    g.PythonTypeToDBType = lambda x : x
    g.DBTypeToPythonType = lambda x : x
    #g.create_edge_indexes()
    g.make_property('rating')
    g.make_property('rating_date')
    g.make_property('release_year')
    g.make_property('title')

    # Load in all of the movie titles and release years
    print 'Loading movie titles...'
    movie_titles = os.path.join(path, 'movie_titles.txt')
    f = open(movie_titles, 'r')
    for line in f.xreadlines():
        movie_id, release_year, title = line.strip().split(',',2)
        movie = g.add_vertex('M%s' % movie_id)
        g.title[movie] = title
        g.release_year[movie] = int(release_year) if release_year != 'NULL' \
                                                  else None
    g.commit()
    print 'Done'

    # Load in the ratings data
    start = time.time()
    totalbytes = 0
    print 'Loading ratings files'
    rating_files = os.listdir(os.path.join(path, 'training_set'))
    commit_count = 0
    commit_period = 100000
    for i,filename in enumerate(rating_files):

        if i % 10 == 0 and i > 0:
            print '  [Total MB: %s] [Loading %.1f KB/s] [Expansion: %.1f]' % \
                  (totalbytes/1024/1024, 
                   totalbytes/1024/(time.time() - start),
                   os.stat('movies.db3')[6]/float(totalbytes))

        full_name = os.path.join(path, 'training_set', filename) 
        file_bytes = os.stat(full_name)[6]
        totalbytes += file_bytes
        print 'Loading %s [%s/%s, %sKB]...' % \
              (filename,i,len(rating_files),file_bytes/1024)
        f = open(full_name, 'r')
        movie_id = 'M%s' % f.readline()[:-2]
        g.add_vertex(movie_id)
        for line in f.xreadlines():
            user_id, rating, rating_date = line.strip().split(',')
            e = g.add_edge('U%s' % user_id, movie_id)
            g.rating[e] = rating
            g.rating_date[e] = rating_date
 
            commit_count += 1
            if commit_count == commit_period:
                print 'Committing...',
                g.commit()
                print 'done'
                commit_count = 0
    g.commit()


if __name__ == '__main__':
    import sys
    build_graph(sys.argv[1])
