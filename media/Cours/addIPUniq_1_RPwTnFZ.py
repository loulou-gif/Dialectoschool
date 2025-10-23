import mysql.connector

# Établir la connexion à la base de données
conn = mysql.connector.connect(
    host="172.18.0.63",
    user="dev",
    password="kPjb12nx2p",
    database="ip_addr"
)

# Créer un objet de curseur pour exécuter des requêtes SQL
cursor = conn.cursor()

# Boucle pour insérer les adresses IP
for i in range(58, 254):
    ip_address = f'196.201.67.{i}'
    query_check = f"SELECT * FROM `ip_addr_uniq` WHERE `ip_address` = '{ip_address}'"

    # Vérifier si l'adresse IP existe déjà dans la table
    cursor.execute(query_check)
    result = cursor.fetchone()

    # Si l'adresse IP n'existe pas, l'insérer dans la table
    if not result:
        query_insert = (f"INSERT INTO `ip_addr_uniq` (`ip_address`, `attributed`, `mask`, `in_pool_addr`, `nd`, "
                        f"`id_ip`, `reservation_number`, `statut`,`type_addr_ip`,`created_at`) VALUES ('{ip_address}', b'0', '255.255.255.0', b'0', '', 3667, '1', 'Disponible','1', NULL);")
        cursor.execute(query_insert)
        conn.commit()
        print(f"Insertion effectuée pour : {ip_address}")
    else:
        print(f"L'adresse IP {ip_address} existe déjà dans la table.")

# Fermer la connexion
conn.close()
