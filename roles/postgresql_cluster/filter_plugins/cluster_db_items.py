
def cluster_db_items(arg):
    cluster_db = []
    for cluster in arg:
        for database in cluster.get('databases', []):
            cluster_db.append(dict(cluster=cluster, database=database))
    return cluster_db

def cluster_user_items(arg):
    cluster_user = []
    for cluster in arg:
        for user in cluster.get('users', []):
            cluster_user.append(dict(cluster=cluster, user=user))
    return cluster_user

class FilterModule(object):
    def filters(self):
        return {'cluster_db_items': cluster_db_items,
                'cluster_user_items': cluster_user_items}
