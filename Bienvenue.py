import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from streamlit_folium import folium_static


# Charger les données
df = pd.read_csv("comptage velo corrected.csv")

# Convertir la colonne 'Date comptage' en datetime si elle n'est pas déjà de ce type
df['Date comptage'] = pd.to_datetime(df['Date comptage'])
    
# Extraire la date sans l'heure
df['Date'] = df['Date comptage'].dt.date
    
# Agréger les données par jour
daily_sum = df.groupby('Date').agg({'Comptage horaire': 'sum'}).reset_index()

# Configuration de la page
st.set_page_config(
    page_title="Vélos à Paris",
    page_icon="🚲",
)

# Titre principal
st.title("🚲 :blue[Trafic cycliste à Paris]")

# Barre latérale avec les options de page
st.sidebar.title("Sommaire")
pages = ["Introduction", "Exploration des données", "Visualisation", "Modélisation", "Conclusion"]
page = st.sidebar.radio("Etapes", pages)

#Nom des contributeurs
st.sidebar.title("Contributeurs")
st.sidebar.markdown("[Cintyha Dina](https://www.linkedin.com/in/cintyha-dina-98396a97/)")
st.sidebar.markdown("[Pascal Paineau](https://www.linkedin.com/in/papaineau72/)")
st.sidebar.markdown("[Stephane Moisan](https://www.exemple.com)")#lien à ajouter

# Logique pour afficher différentes pages
if page == "Introduction":
    st.write("### :blue[Introduction]")
    st.image("paris-velo.jpg")
    st.markdown(
        """
        Le projet que nous vous présentons aujourd'hui est une analyse des données collectées à partir des compteurs à vélo permanents que la Ville de Paris déploie depuis plusieurs années déjà afin d’évaluer le développement de la pratique cycliste.
        
        **👈 Vous trouverez sur le volet à gauche les différentes étapes de notre analyse.**
        
        ### :blue[Objectifs]
        
        Notre principal objectif est de donner une vue d'ensemble de l'usage du vélo à Paris et de faire émerger des tendances afin d'aider à la prise de décision quant à l'aménagement des pistes cyclables et les possibilités d'investissement dans ce moyen de transport moins polluant que la voiture.
        """
    )
elif page == "Exploration des données":
    st.write("### :blue[Exploration des données]")
    st.dataframe(df.head(10))
elif page == "Visualisation":
    st.write("### :blue[Visualisation des données]")
    st.markdown("### Présentation du trafic cycliste à Paris")
    
    selectbox = st.selectbox ("**Eléments d'analyse visuelle :**", ("Choisir un graphique", "Evolution de l'installation des compteurs par année", "Evolution du nombre de kilomètres aménagés","Répartition des compteurs dans la ville", "Affichage des compteurs selon le nombre de passage"))
    if selectbox == "Evolution de l'installation des compteurs par année" :
        # Convertir les colonnes de dates en type datetime
        df['Date comptage'] = pd.to_datetime(df['Date comptage'])
        df['Date installation'] = pd.to_datetime(df['Date installation'])

        # Extraire l'année d'installation des compteurs
        df['Annee installation'] = df['Date installation'].dt.year

        # Compter le nombre de compteurs installés par année
        counts_by_year = df['Annee installation'].value_counts().sort_index()

        # Visualiser le nombre de compteurs installés par année
        st.write("Nombre de compteurs installés chaque année :")
        st.bar_chart(counts_by_year)

    import matplotlib.pyplot as plt

    if selectbox == "Evolution du nombre de kilomètres aménagés":
        Ev_res = {
            "Année": [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022],
            "Linéaire en km": [292.8, 327.3, 370.9, 399.3, 439.5, 446.2, 647.5, 654.8, 677, 732.5, 737.5, 742.1, 779.8, 835.6, 912.6, 1037.05, 1136.3, 1170.8, 1202.5]
        }
        df_piste = pd.DataFrame(Ev_res)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        df_piste.plot(kind="bar", x="Année", y="Linéaire en km", width=0.7, color="blue", ax=ax)
        
        ax.set_title("Evolution du nombre de kilomètres aménagés", fontsize=14, fontweight='bold')
        ax.set_xlabel('Année')
        ax.set_ylabel('Nombre de kilomètres aménagés')
        ax.tick_params(axis='x', rotation=45)
        
        st.pyplot(fig) 

    
   

    if selectbox == "Répartition des compteurs dans la ville":
        df_plan = df.drop_duplicates(subset="Nom du compteur", keep='first')

        # Créer la carte avec Folium
        paris = folium.Map(location=[48.856578, 2.351828], zoom_start=11)

        # Ajouter une couche
        folium.TileLayer('openstreetmap').add_to(paris)

        # Ajouter un marqueur pour chaque compteur
        for index, row in df_plan.iterrows():
            folium.Marker(location=[row["Latitude"], row["Longitude"]],
                        popup=row["Nom du compteur"],
                        tooltip="Cliquez ici pour voir le nom du compteur").add_to(paris)

        # Ajouter un contrôle de couches à la carte
        folium.LayerControl().add_to(paris)

        # Afficher la carte Folium dans Streamlit
        folium_static(paris)


    

    if selectbox == "Affichage des compteurs selon le nombre de passage":
        # Créer la carte avec Folium
        paris = folium.Map(location=[48.856578, 2.351828], zoom_start=13, min_zoom=12, max_zoom=18)

        # Grouper les données par compteur et calculer la somme des passages
        df_plan_sum = df.groupby(['Nom du compteur', "Latitude", "Longitude"])['Comptage horaire'].sum().reset_index()

        # Définir la couleur en fonction du nombre de passages
        def colorer_zone(comptage):
            if comptage > seuil:
                return 'red'  # zones avec plus de passages en rouge
            else:
                return 'green'  # zones avec moins de passages en vert

        # Définir le seuil pour différencier les zones avec plus ou moins de passages
        seuil = df_plan_sum['Comptage horaire'].quantile(0.75)  # par exemple, seuil à 75ème percentile

        # Ajouter des marqueurs de cercle pour chaque zone avec couleur basée sur le nombre de passages
        for index, row in df_plan_sum.iterrows():
            folium.CircleMarker(location=[row["Latitude"], row["Longitude"]],
                                popup=row["Comptage horaire"],
                                radius=row["Comptage horaire"] / 100000,
                                fill=True,
                                color=colorer_zone(row["Comptage horaire"]),
                                tooltip="Cliquez ici pour voir le nombre de passage").add_to(paris)

        # Afficher la carte Folium dans Streamlit
        folium_static(paris)



#Visualisation du trafic en fonction de la temporalité
    temporalite = st.radio('**Nombre de passage des vélos sur quelle période ?**', ('Jour', 'Semaine', 'Mois', 'Année'), index=None)
    if temporalite == 'Jour':
        df_graph = df.copy()
        df_graph['Heure comptage']=(df_graph['Date comptage'].dt.time)
        df_graph = df_graph[['Heure comptage', 'Comptage horaire']]
        df_compt_hour = df_graph.groupby("Heure comptage").mean()
        fig, ax = plt.subplots(figsize=(10, 6))
        df_compt_hour.plot(kind='bar', color='green', ax=ax)
        plt.title("Sur une journée", fontsize=14, fontweight='bold')
        plt.xlabel('Heure de comptage')
        plt.ylabel('Moyenne des passages')
        plt.xticks(rotation=45)
        plt.tight_layout()  
        st.pyplot(fig)

    if temporalite == "Mois" :
        df_graph = df.copy()
        df_graph = df_graph[(df_graph['Date comptage']>='2023-04-01') & (df_graph['Date comptage']<'2023-05-01')]
        hebdo_sum = df_graph.groupby(df_graph['Date comptage'].dt.to_period("d")).agg({'Comptage horaire': 'sum'}).reset_index()
        fig = plt.figure(figsize=(10, 6))
        x=hebdo_sum['Date comptage'].dt.start_time
        y=hebdo_sum['Comptage horaire']
        plt.plot(x, y,linestyle='-', marker='o')
        plt.title("Sur le mois d'avril 2023",fontsize=14,fontweight='bold')
        plt.xlabel('Jour')
        plt.ylabel('Nombre de comptage')
        plt.xticks(rotation=45)
        plt.annotate(
            'Week-end',fontweight='bold',color='green', xy=(110, 140), xytext=(120, 100),xycoords='figure points',
                    arrowprops=dict(facecolor='green', shrink=0.05))
        plt.annotate(
            '',fontweight='bold',color='green', xy=(250, 100), xytext=(180, 105),xycoords='figure points',
                    arrowprops=dict(facecolor='green', shrink=0.05))
        plt.annotate(
            'Grèves',fontweight='bold',color='red', xy=(290, 260), xytext=(280, 110),xycoords='figure points',
                    arrowprops=dict(facecolor='red', shrink=0.05))
        plt.annotate(
            '',fontweight='bold',color='red', xy=(335, 180), xytext=(320, 125),xycoords='figure points',
                    arrowprops=dict(facecolor='red', shrink=0.05))
        plt.annotate(
            '',fontweight='bold',color='red', xy=(480, 90), xytext=(320, 110),xycoords='figure points',
                    arrowprops=dict(facecolor='red', shrink=0.05))
        plt.annotate(
            'Week-end',fontweight='bold',color='green', xy=(340, 190), xytext=(390, 170),xycoords='figure points',
                    arrowprops=dict(facecolor='green', shrink=0.05))
        plt.annotate(
            'Week-end',fontweight='bold',color='green', xy=(480, 100), xytext=(520, 100),xycoords='figure points',
                    arrowprops=dict(facecolor='green', shrink=0.05))
        st.pyplot(fig)


    if temporalite == "Année":
        
        df_graph = df.copy()
        df_graph['Jour'] = df_graph['Date comptage'].dt.strftime('%Y-%m-%d')
        df_graph['Mois'] = df_graph['Date comptage'].dt.strftime('%Y-%m')
        monthly_sum = df_graph.groupby('Mois')['Comptage horaire'].sum().reset_index()

        # Créer un graphique à barres
        fig, ax = plt.subplots(figsize=(10, 6))
        x = monthly_sum['Mois']
        y = monthly_sum['Comptage horaire']
        ax.bar(x, y, width=0.9, alpha=0.5, color=['blue', 'blue', 'blue', 'green', 'green', 'green', 'yellow', 'yellow', 'yellow', 'orange', 'orange', 'orange'])
        
        def addlabels(x,y):
            for i in range(len(x)):
                plt.text(i, y[i], y[i], ha='center',
                bbox=dict(facecolor='red', alpha=.2), fontsize=8, fontweight='bold')

        addlabels(x, y)
        plt.title('Sur une année', fontweight='bold')
        plt.xlabel('Mois')
        plt.ylabel('Nombre de comptage')
        plt.xticks(rotation=45)

        # Ajouter des annotations avec des flèches
        ax.annotate('Vacances de Noël', fontweight='bold', color='royalblue', xy=(290, 220), xytext=(300, 300), xycoords='figure points',
                    arrowprops=dict(facecolor='fuchsia', shrink=0.05))
        ax.annotate('Vacances d\'été', fontweight='bold', color='royalblue', xy=(120, 250), xytext=(70, 350), xycoords='figure points',
                    arrowprops=dict(facecolor='fuchsia', shrink=0.05))
        ax.annotate('Jours fériés et ponts', fontweight='bold', color='royalblue', xy=(460, 310), xytext=(380, 350), xycoords='figure points',
                    arrowprops=dict(facecolor='fuchsia', shrink=0.05))

        st.pyplot(fig)




    import calendar

    if temporalite == "Semaine":
        df_graph = df.copy()
        
        # Filtrer les données pour ne considérer que la première semaine de juin
        first_week_june = df_graph[(df_graph['Date comptage'].dt.month == 6) & (df_graph['Date comptage'].dt.day >= 1) & (df_graph['Date comptage'].dt.day <= 7)]
        
        # Grouper par jour et calculer le nombre total de passages de vélos pour chaque jour
        passages_per_day = first_week_june.groupby(df_graph['Date comptage'].dt.dayofweek).agg({'Comptage horaire': 'sum'}).reset_index()
        
        # Convertir le numéro du jour en nom complet du jour de la semaine en français
        jours_semaine_fr = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
        passages_per_day['Jour de la semaine'] = passages_per_day['Date comptage'].apply(lambda x: jours_semaine_fr[x])
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(passages_per_day['Jour de la semaine'], passages_per_day['Comptage horaire'], color='blue')
        ax.set_title('Sur la première semaine de juin', fontsize=14, fontweight='bold')
        ax.set_xlabel('Jours de la semaine')
        ax.set_ylabel('Nombre de passages de vélos')
        ax.tick_params(axis='x', rotation=45)  # Rotation des dates pour une meilleure lisibilité
        
        st.pyplot(fig)



elif page == "Modélisation":
    st.write("Page de modélisation")
    # Ajoutez ici votre code de modélisation
elif page == "Conclusion":
    st.write("Conclusion")
    # Ajoutez ici votre conclusion ou vos résultats finaux

