from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base










# Leg de verbinding tussen die Python-bouwtekening (hierboven) en het echte bestand op je harde schijf (gym_membership.db).

#The engine drives to the Database-file
DATABASE_URL = "sqlite:///gym_membership.db"

# engine (De Vrachtwagen): Dit is de motor die de weg weet naar je database-bestand. Hij zorgt dat de verbinding fysiek tot stand komt.
engine = create_engine(DATABASE_URL)

# SessionLocal (De Lopende Band):
# Dit is de fabriek die strakjes tijdelijke, unieke sessies (lopende banden) gaat aanmaken voor elke klant die de website bezoekt.
# This factory will create the sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)






# De basis bouw-tekening voor de ORM-modellen
base = declarative_base()






# de automatische sluis (portier)
def get_db():

    # Pak een verse lopende band uit de fabriek
    db = SessionLocal()

    try:
        # Geef de database tijdelijk weg aan de route die erom vraagt
        yield db
    finally:
        # Wanneer de route klaar is, sluit deze regel de sluis af
        db.close()