// (function () {

// ```
// function escapeHTML(value) {
//     return String(value || "")
//         .replace(/&/g, "&amp;")
//         .replace(/</g, "&lt;")
//         .replace(/>/g, "&gt;")
//         .replace(/"/g, "&quot;")
//         .replace(/'/g, "&#039;");
// }


// window.festivalToast = function (
//     type = "info",
//     title = "Festival Wishes",
//     message = "",
//     duration = 4500
// ) {

//     let container = document.querySelector(".fw-toast-container");

//     if (!container) {

//         container = document.createElement("div");

//         container.className = "fw-toast-container";

//         document.body.appendChild(container);
//     }


//     const toast = document.createElement("div");

//     toast.className = "fw-toast " + type;


//     let icon = "💡";


//     if (type === "success") {
//         icon = "✓";
//     }

//     else if (type === "error") {
//         icon = "✕";
//     }

//     else if (type === "warning") {
//         icon = "⚠";
//     }


//     toast.innerHTML = `

//         <div class="fw-toast-icon">
//             ${icon}
//         </div>

//         <div class="fw-toast-content">

//             <div class="fw-toast-title">
//                 ${escapeHTML(title)}
//             </div>

//             <div class="fw-toast-message">
//                 ${escapeHTML(message)}
//             </div>

//         </div>

//         <button
//             type="button"
//             class="fw-toast-close"
//             aria-label="Close"
//         >
//             ×
//         </button>

//         <div class="fw-toast-progress"></div>

//     `;


//     container.appendChild(toast);


//     const progress =
//         toast.querySelector(".fw-toast-progress");


//     progress.style.animationDuration =
//         duration + "ms";


//     // Start animation
//     requestAnimationFrame(function () {

//         toast.classList.add("show");

//     });


//     const closeButton =
//         toast.querySelector(".fw-toast-close");


//     closeButton.addEventListener(
//         "click",
//         function () {

//             removeToast();

//         }
//     );


//     const timer = setTimeout(
//         function () {

//             removeToast();

//         },
//         duration
//     );


//     function removeToast() {

//         clearTimeout(timer);

//         toast.classList.remove("show");

//         toast.classList.add("hide");


//         setTimeout(
//             function () {

//                 if (toast.parentNode) {
//                     toast.remove();
//                 }

//                 if (
//                     container &&
//                     container.children.length === 0
//                 ) {
//                     container.remove();
//                 }

//             },
//             350
//         );

//     }

// };


// // ==========================================
// // SHORTCUTS
// // ==========================================

// window.festivalSuccess =
//     function (title, message, duration) {

//         festivalToast(
//             "success",
//             title,
//             message,
//             duration
//         );

//     };


// window.festivalError =
//     function (title, message, duration) {

//         festivalToast(
//             "error",
//             title,
//             message,
//             duration
//         );

//     };


// window.festivalWarning =
//     function (title, message, duration) {

//         festivalToast(
//             "warning",
//             title,
//             message,
//             duration
//         );

//     };


// window.festivalInfo =
//     function (title, message, duration) {

//         festivalToast(
//             "info",
//             title,
//             message,
//             duration
//         );

//     };


// // ==========================================
// // URL TOAST
// // ==========================================

// function festivalToastFromURL() {

//     const params =
//         new URLSearchParams(
//             window.location.search
//         );


//     console.log(
//         "Festival Toast: JS loaded"
//     );


//     console.log(
//         "Festival Toast: URL =",
//         window.location.href
//     );


//     // SIGNUP
//     if (
//         params.get("signup") === "success"
//     ) {

//         festivalSuccess(
//             "Account Created 🎉",
//             "Your dashboard account has been created successfully."
//         );

//     }


//     // LOGIN
//     else if (
//         params.get("login") === "success"
//     ) {

//         festivalSuccess(
//             "Welcome Back 👋",
//             "You have logged in successfully."
//         );

//     }


//     // LOGOUT
//     else if (
//         params.get("logout") === "success"
//     ) {

//         festivalSuccess(
//             "Logged Out",
//             "You have been logged out successfully."
//         );

//     }


//     // PASSWORD CHANGED
//     else if (
//         params.get("password") === "changed"
//     ) {

//         festivalSuccess(
//             "Password Changed 🔐",
//             "Your password has been changed successfully."
//         );

//     }


//     // RESET EMAIL
//     else if (
//         params.get("reset") === "sent"
//     ) {

//         festivalSuccess(
//             "Email Sent ✉️",
//             "If this email exists, a password reset link has been sent."
//         );

//     }


//     // RESET SUCCESS
//     else if (
//         params.get("reset") === "success"
//     ) {

//         festivalSuccess(
//             "Password Reset 🎉",
//             "Your password has been reset successfully."
//         );

//     }


//     // RESET EXPIRED
//     else if (
//         params.get("reset") === "expired"
//     ) {

//         festivalError(
//             "Link Expired",
//             "Your password reset link has expired."
//         );

//     }


//     // RESET INVALID
//     else if (
//         params.get("reset") === "invalid"
//     ) {

//         festivalError(
//             "Invalid Link",
//             "This password reset link is invalid."
//         );

//     }


//     // ======================================
//     // CLEAN URL
//     // ======================================

//     if (
//         params.has("signup") ||
//         params.has("login") ||
//         params.has("logout") ||
//         params.has("password") ||
//         params.has("reset")
//     ) {

//         const cleanURL =
//             window.location.pathname;


//         window.history.replaceState(
//             {},
//             document.title,
//             cleanURL
//         );

//     }

// }


// // ==========================================
// // INITIALIZE
// // ==========================================

// if (
//     document.readyState === "loading"
// ) {

//     document.addEventListener(
//         "DOMContentLoaded",
//         festivalToastFromURL
//     );

// }

// else {

//     festivalToastFromURL();

// }
// ```

// })();











// const selectAll = document.getElementById(
//     "selectAll"
// );


// const checkboxes = document.querySelectorAll(
//     ".festival-checkbox"
// );


// const selectedCount = document.getElementById(
//     "selectedCount"
// );


// function updateSelectedCount(){

//     let count = 0;


//     checkboxes.forEach(

//         function(checkbox){

//             if(checkbox.checked){

//                 count++;

//             }

//         }

//     );


//     selectedCount.textContent = count;

// }


// if(selectAll){

//     selectAll.addEventListener(

//         "change",

//         function(){

//             checkboxes.forEach(

//                 function(checkbox){

//                     checkbox.checked =
//                         selectAll.checked;

//                 }

//             );


//             updateSelectedCount();

//         }

//     );

// }


// checkboxes.forEach(

//     function(checkbox){

//         checkbox.addEventListener(

//             "change",

//             function(){

//                 updateSelectedCount();


//                 selectAll.checked =

//                     document.querySelectorAll(
//                         ".festival-checkbox:checked"
//                     ).length ===

//                     checkboxes.length;

//             }

//         );

//     }

// );


// /* =====================================================
//    BULK ACTION CONFIRMATION
// ===================================================== */


// const bulkForm = document.getElementById(
//     "bulkForm"
// );


// if(bulkForm){

//     bulkForm.addEventListener(

//         "submit",

//         function(event){

//             const selected =

//                 document.querySelectorAll(
//                     ".festival-checkbox:checked"
//                 );


//             const action =

//                 document.getElementById(
//                     "bulkAction"
//                 ).value;


//             if(selected.length === 0){

//                 event.preventDefault();

//                 festivalWarning(

//                     "No Festival Selected",

//                     "Please select at least one festival."

//                 );

//                 return;

//             }


//             if(!action){

//                 event.preventDefault();

//                 festivalWarning(

//                     "Select Action",

//                     "Please choose a bulk action."

//                 );

//                 return;

//             }


//             if(action === "delete"){

//                 const confirmDelete = confirm(

//                     "Are you sure you want to delete " +

//                     selected.length +

//                     " festival(s)?"

//                 );


//                 if(!confirmDelete){

//                     event.preventDefault();

//                 }

//             }

//         }

//     );

// }



function festivalToastFromURL() {

    const params = new URLSearchParams(window.location.search);

    const toast = params.get("toast");

    if (!toast) {
        return;
    }


    if (toast === "created") {

        festivalSuccess(
            "Festival Created 🎉",
            "Festival has been added successfully."
        );

    }


    else if (toast === "updated") {

        festivalSuccess(
            "Festival Updated ✨",
            "Festival details have been updated successfully."
        );

    }


    else if (toast === "deleted") {

        festivalSuccess(
            "Festival Deleted 🗑️",
            "Festival has been deleted successfully."
        );

    }


    else if (toast === "bulk_trending") {

        festivalSuccess(
            "Festivals Updated 🔥",
            "Selected festivals are now trending."
        );

    }


    else if (toast === "bulk_normal") {

        festivalInfo(
            "Trending Removed",
            "Selected festivals are no longer trending."
        );

    }


    else if (toast === "bulk_deleted") {

        festivalSuccess(
            "Festivals Deleted 🗑️",
            "Selected festivals have been deleted."
        );

    }


    else if (toast === "none") {

        festivalWarning(
            "Nothing Selected",
            "Please select at least one festival."
        );

    }


    // Remove toast parameter from URL

    params.delete("toast");

    const newURL =
        window.location.pathname +
        (params.toString()
            ? "?" + params.toString()
            : "");

    window.history.replaceState(
        {},
        document.title,
        newURL
    );
}




/* =====================================================
   FESTIVAL TOAST SYSTEM
===================================================== */

function festivalToast(
    type,
    title,
    message,
    duration = 4000
) {

    const existingToast =
        document.querySelector(".festival-toast");

    if (existingToast) {
        existingToast.remove();
    }


    /* ICONS */

    const icons = {

        success: "✓",

        error: "✕",

        warning: "!",

        info: "i"

    };


    const icon =
        icons[type] || icons.info;


    /* CREATE */

    const toast =
        document.createElement("div");

    toast.className =
        `festival-toast ${type}`;


    toast.style.setProperty(
        "--toast-duration",
        `${duration}ms`
    );


    toast.innerHTML = `

        <div class="festival-toast-icon">
            ${icon}
        </div>

        <div class="festival-toast-content">

            <div class="festival-toast-title">
                ${title}
            </div>

            <div class="festival-toast-message">
                ${message}
            </div>

        </div>

        <button
            type="button"
            class="festival-toast-close"
            aria-label="Close">
            ×
        </button>

        <div class="festival-toast-progress"></div>

    `;


    document.body.appendChild(toast);


    /* CLOSE BUTTON */

    const closeButton =
        toast.querySelector(
            ".festival-toast-close"
        );


    closeButton.addEventListener(
        "click",
        function () {

            removeFestivalToast(toast);

        }
    );


    /* AUTO CLOSE */

    const timer =
        setTimeout(
            function () {

                removeFestivalToast(toast);

            },
            duration
        );


    toast.dataset.timer = timer;

}


/* =====================================================
   REMOVE
===================================================== */

function removeFestivalToast(toast) {

    if (!toast) {
        return;
    }


    toast.style.animation =
        "festivalToastOut 0.35s ease forwards";


    setTimeout(
        function () {

            if (toast) {
                toast.remove();
            }

        },
        350
    );

}


/* =====================================================
   SHORTCUTS
===================================================== */

function festivalSuccess(
    title,
    message,
    duration = 4000
) {

    festivalToast(
        "success",
        title,
        message,
        duration
    );

}


function festivalError(
    title,
    message,
    duration = 5000
) {

    festivalToast(
        "error",
        title,
        message,
        duration
    );

}


function festivalWarning(
    title,
    message,
    duration = 4500
) {

    festivalToast(
        "warning",
        title,
        message,
        duration
    );

}


function festivalInfo(
    title,
    message,
    duration = 4000
) {

    festivalToast(
        "info",
        title,
        message,
        duration
    );

}


/* =====================================================
   URL TOAST
===================================================== */

function festivalToastFromURL() {

    const params =
        new URLSearchParams(
            window.location.search
        );


    const toast =
        params.get("toast");


    if (!toast) {
        return;
    }


    switch (toast) {


        /* FESTIVAL CREATED */

        case "created":

            festivalSuccess(
                "Festival Created 🎉",
                "Festival has been added successfully."
            );

            break;


        /* FESTIVAL UPDATED */

        case "updated":

            festivalSuccess(
                "Festival Updated ✨",
                "Festival details have been updated successfully."
            );

            break;


        /* FESTIVAL DELETED */

        case "deleted":

            festivalSuccess(
                "Festival Deleted 🗑️",
                "Festival has been deleted successfully."
            );

            break;


        /* BULK TRENDING */

        case "bulk_trending":

            festivalSuccess(
                "Trending Updated 🔥",
                "Selected festivals are now trending."
            );

            break;


        /* BULK NORMAL */

        case "bulk_normal":

            festivalInfo(
                "Trending Removed",
                "Selected festivals are no longer trending."
            );

            break;


        /* BULK DELETE */

        case "bulk_deleted":

            festivalSuccess(
                "Festivals Deleted 🗑️",
                "Selected festivals have been deleted successfully."
            );

            break;


        /* NOTHING SELECTED */

        case "none":

            festivalWarning(
                "Nothing Selected",
                "Please select at least one festival."
            );

            break;


        /* LOGIN */

        case "login":

            festivalSuccess(
                "Welcome Back 👋",
                "You have logged in successfully."
            );

            break;


        /* SIGNUP */

        case "signup":

            festivalSuccess(
                "Account Created 🎉",
                "Your admin account has been created successfully."
            );

            break;


        /* LOGOUT */

        case "logout":

            festivalInfo(
                "Logged Out 👋",
                "You have been logged out successfully."
            );

            break;


        /* ERROR */

        case "error":

            festivalError(
                "Something Went Wrong",
                "Please try again."
            );

            break;

    }


    /* REMOVE TOAST FROM URL */

    params.delete("toast");


    const newURL =
        window.location.pathname +
        (
            params.toString()
                ? "?" + params.toString()
                : ""
        );


    window.history.replaceState(
        {},
        document.title,
        newURL
    );

}


/* =====================================================
   AUTO START
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        festivalToastFromURL();

    }
);



/* =========================================================
   STATUS TOGGLE CONFIRMATION
========================================================= */

const statusForms =
    document.querySelectorAll(".status-form");


statusForms.forEach(
    function(form){

        form.addEventListener(
            "submit",
            function(event){

                const button =
                    form.querySelector("button");


                const isDeactivate =
                    button.classList.contains(
                        "btn-deactivate"
                    );


                let message;


                if(isDeactivate){

                    message =
                        "Deactivate this festival? " +
                        "Its page can be hidden from active festival listings.";

                }
                else{

                    message =
                        "Activate this festival? " +
                        "It will become available again.";

                }


                if(
                    !confirm(message)
                ){

                    event.preventDefault();

                }

            }
        );

    }
);



document.querySelectorAll(".copy-link").forEach(
    function(button){

        button.addEventListener(
            "click",
            async function(){

                const link =
                    button.dataset.link;

                try{

                    await navigator.clipboard.writeText(
                        link
                    );

                    if(
                        typeof festivalSuccess ===
                        "function"
                    ){

                        festivalSuccess(
                            "Link Copied",
                            "Wish link copied successfully."
                        );

                    }else{

                        alert(
                            "Wish link copied!"
                        );

                    }

                }catch(error){

                    prompt(
                        "Copy this wish link:",
                        link
                    );

                }

            }
        );

    }
);

