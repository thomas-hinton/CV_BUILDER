function isValidString(str){
    /*
    Verify if string is valid : only letters, accents and hyphens allowed
    param: str : string to verify
    return: true if valid, false otherwise
    */

    const clean = str.trim();
    return /^[A-Za-zÀ-ÖØ-öø-ÿ-]+$/.test(clean);
}

async function modifyName() {
    /*
    Modify and store username in DB
    */

    const nameInput = document.getElementById("name");
    const name = nameInput.value.trim(); //Sanitize

    if (name) {
        
        if(isValidString(name)){

            //Call to endpoint
            try {
                const response = await fetch(
                `http://127.0.0.1:8000/modify_name?name=${encodeURIComponent(name)}`,
                { method: "POST" }
                );

                if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
                }

                const data = await response.json();
                console.log(data);

                // Stored in localstorage for reload purpose
                localStorage.setItem("name", name);

            } catch (err) {
                console.error(err);
            }    
        }
    } else {
        alert("Le nom n'est pas valide !");
    }
}


document.addEventListener("DOMContentLoaded", () => {

    const btnModifyName = document.getElementById("modify-name");
    const btnModifySurname = document.getElementById("modify-surname");
    const btnModifyEmail = document.getElementById("modify-email");
    const btnModifyPhone = document.getElementById("modify-phone");

    btnModifyName.addEventListener("click", modifyName);
  });


