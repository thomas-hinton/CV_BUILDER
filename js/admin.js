function isValidString(str){
    /*
    Verify if string is valid : only letters, accents and hyphens allowed
    param: str : string to verify
    return: true if valid, false otherwise
    */

    const clean = str.trim();
    return /^[A-Za-zÀ-ÖØ-öø-ÿ-]+$/.test(clean);
}

async function getDataBaseInfosFromLocalStorage(name) {
    /*
    Getting all database info from local storage data
    Only name for now but will be extended to other data in the future
    */

    if (name) {
        
        if(isValidString(name)){

            //Call to endpoint
            try {
                const response = await fetch(
                `http://127.0.0.1:8000/get_user_by_name?name=${encodeURIComponent(name)}`,
                { method: "GET" }
                );

                if (!response.ok) {
                throw new Error(`Erreur HTTP ${response.status}`);
                }

                const data = await response.json();
                console.log(data);

                //At this point we only do it for name in dev phase
                return data;

            } catch (err) {
                console.error(err);
            }    
        }
    } else {
        alert("Le nom n'est pas valide !");
    }
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
                return null;
            }    
        }
    } else {
        alert("Le nom n'est pas valide !");
    }
}

async function getInputFilledWithLocalStorage(){
    /*
    Gets infos from DB by calling endpoints related to data stored in localStorage
    */

    const localName = localStorage.getItem("name");

    if(localName){

        // Recleaning it even if it is done already, just in case localStorage is set manually
        cleanName = localName.trim();
        if(isValidString(cleanName)){
            
            name_to_fill = await getDataBaseInfosFromLocalStorage(cleanName)
            console.log("Name to fill : ", name_to_fill);

            if (name_to_fill && name_to_fill.status === "found" && Array.isArray(name_to_fill.data)) {
                document.getElementById("name").value = name_to_fill.data[1] ?? "";
            }

        } else {
            console.warn("Invalid name in localStorage, skipping the filling of the input");
        }

    }

}


document.addEventListener("DOMContentLoaded", () => {

    // Automatically filling inputs with localStorage data
    getInputFilledWithLocalStorage();

    const btnModifyName = document.getElementById("modify-name");
    const btnModifySurname = document.getElementById("modify-surname");
    const btnModifyEmail = document.getElementById("modify-email");
    const btnModifyPhone = document.getElementById("modify-phone");

    btnModifyName.addEventListener("click", modifyName);
  });


