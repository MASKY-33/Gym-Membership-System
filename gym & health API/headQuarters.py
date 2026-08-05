from fastapi import FastAPI, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse


import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


# Imorteer de onderdelen uit de files
from motorForDB import engine, base, get_db
from DB_tables import GymMemberDB
from incomingDataGuard import Membership









# --- JWT CONFIGUATIE (De geheimen van de server) ---
SECRET_KEY = "password_nobody_mayno_agence_573"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10



# 2. De portier van FastAPI (OAuth2)
# De automatische portier die zoekt naar het token (keycard) in de HTTP Headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



# 3. De controle sluis (De Portier)
def check_if_user_is_logged_in(token: str = Depends(oauth2_scheme)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        Username = data.get("sub")
        return Username

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Your keycard has expired! Login again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid keycard")







base.metadata.create_all(bind=engine)







# Activate api/fastapi routes-HTTP-requests
app = FastAPI()



# Dit vangt elke onverwachte fout (Exception) op in je hele application
@app.exception_handler(Exception)
def universal_error_handler(request: Request, exc: Exception):


    # Hier log je de echte, technische fout voor jezelf in de Terminal
    # Zo weet jij als Software-Engineer precies wat er onder de motorkap misging
    print(f"Alarm! An unexpected error has occurred: {str(exc)}")


    # Dit stuur je terug naar de klant: een schone, professionele JSON-message
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error has occurred in our system. Our technicians are working on a solution!"
        }
    )










# --- Route 1. DE INLOGPOORT (Token Uitdelen) ---
# Hier komt de klant met zijn username en password
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Simpele controle (normaal check je de database)
    if form_data.username == "MASKY" and form_data.password == "MASKY344":

        # Password is correct! Maak de payload (De inhoud van de keycard)
        payload = {
            "sub": form_data.username,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }

        # Druk de lakzegel erop met de SECRET_KEY
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        # Geef de keycard terug aan de klant
        return {"access_token": token, "token_type": "bearer"}

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password"
        )











#  Gym-API

@app.post("/gym_subscription", response_model=Membership)
def subscription_port(
    subscription: Membership,
    db: Session = Depends(get_db),
    username: str = Depends(check_if_user_is_logged_in)  # <-- alleen de ingelogde persoon mag en kan nieuwe members aanmaken
):  # Doe een aanvraag om de database te mogen gebruiken

    if subscription.is_active:
        # Translate the Pydantic data into the ORM-model (GymMemberDB) to store it in the database
        db_member = GymMemberDB(
            name=subscription.name,
            age=subscription.age,
            is_active=subscription.is_active
        )

        # Leg het model op de lopende band van de database
        db.add(db_member)
        # Definitief opslaan volgense de ACID
        db.commit()
        # Refresh het object zodat de database het ID_nummer meegeeft
        db.refresh(db_member)

        # Na deze return actie wordt alles geregeld met name het sluiten van de database-verbinding en het teruggeven van de data aan de gebruiker
        return db_member
    else:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied! Unfortunately {subscription.name}, renew your subscription!"
        )












# Weather-API

@app.get("/weather")
def check_weather(weather: float):

    if weather >= 25:
        return {"Summerday": "Enjoy your outside training!"}
    elif weather >= 10:
        return {"Normal weather": "Put on a shirt or something like that."}
    else:
        return {"It's freezing!": "Put on something warm."}














# Take member by id to take a look (read)
# Take out info from one member
@app.get("/gym_subscription/{member_id}", response_model=Membership)
def show_member_by_id(
    member_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(check_if_user_is_logged_in)  # <-- alleen de ingelogde persoon mag en kan de data (members) bekijken
):  # doe een aanvraag om de database te mogen gebruiken om members te mogen bekijken

    # Start de zoekemachine via de ORM-vertaalmachine en zoek het lid op basis van het id-nummer
    member = db.query(GymMemberDB).filter(GymMemberDB.id == member_id).first()

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    # Na deze return actie wordt alles geregeld met name het sluiten van de database-verbinding en het teruggeven van de data aan de gebruiker
    return member















# Delete a member fully
# P.S.) Changed delete-route
@app.delete("/gym_subscription/{member_id}")
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    username: str = Depends(check_if_user_is_logged_in)  # <-- Hier is de portier!
):  # doe een aanvraag om de database te mogen gebruiken om een member te mogen verwijderen

    member = db.query(GymMemberDB).filter(GymMemberDB.id == member_id).first()

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found!")


    db.delete(member)  # <-- If member exists, delete it from the database
    db.commit()  # <-- ACID commit

    return{"member_id": member_id, "status": "Deleted successfully", "deleted_by": username}
