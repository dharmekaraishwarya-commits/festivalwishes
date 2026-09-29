/* =====================================================
   PRELOADER
===================================================== */

window.addEventListener("load", function () {

    const preloader =
        document.getElementById("js-preloader");

    setTimeout(function () {

        preloader.classList.add("hide");

    }, 400);

});



/* =====================================================
   MOBILE MENU
===================================================== */

function toggleMenu() {

    const menu =
        document.getElementById("festivalNav");

    menu.classList.toggle("show");

}


/* Close menu after clicking link */

document.querySelectorAll(
    "#festivalNav a"
).forEach(function(link) {

    link.addEventListener(
        "click",
        function() {

            if (window.innerWidth < 992) {

                document
                    .getElementById("festivalNav")
                    .classList.remove("show");

            }

        }
    );

});



/* =====================================================
   SEARCH
===================================================== */

const input =
    document.getElementById("searchInput");

const suggestions =
    document.getElementById("suggestions");


if (input) {

    input.addEventListener(
        "keyup",
        function () {

            const query =
                input.value.trim();


            if (query.length < 1) {

                suggestions.innerHTML = "";

                return;

            }


            fetch(
                `/search/?q=${encodeURIComponent(query)}`
            )

            .then(function(response) {

                return response.json();

            })

            .then(function(data) {

                suggestions.innerHTML = "";


                data.forEach(function(item) {

                    const link =
                        document.createElement("a");

                    link.classList.add(
                        "list-group-item",
                        "list-group-item-action"
                    );

                    link.innerText =
                        item.name;

                    link.href =
                        `/generate/${item.slug}/`;

                    suggestions.appendChild(link);

                });

            })

            .catch(function(error) {

                console.error(
                    "Search error:",
                    error
                );

            });

        }
    );


    document.addEventListener(
        "click",
        function(event) {

            if (
                !input.contains(event.target) &&
                !suggestions.contains(event.target)
            ) {

                suggestions.innerHTML = "";

            }

        }
    );

}



/* =====================================================
   LIVE USER COUNTER
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const userCountElement =
            document.getElementById("userCount");


        if (!userCountElement) {
            return;
        }


        let count =
            Math.floor(
                Math.random() * (450 - 280 + 1)
            ) + 280;


        userCountElement.innerText =
            count;


        setInterval(
            function() {

                const change =
                    Math.floor(
                        Math.random() * 9
                    ) - 3;


                count += change;


                if (count < 150) {
                    count += 10;
                }


                if (count > 600) {
                    count -= 10;
                }


                userCountElement.style.opacity = 0;


                setTimeout(
                    function() {

                        userCountElement.innerText =
                            count;

                        userCountElement.style.opacity =
                            1;

                    },
                    300
                );


            },
            Math.floor(
                Math.random() * 3000
            ) + 4000
        );

    }
);



/* =====================================================
   COUNTDOWN TIMERS
===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function() {


        function updateAllTimers() {


            const now =
                new Date().getTime();


            document
                .querySelectorAll(
                    ".festival-timer"
                )
                .forEach(function(timer) {


                    const targetDateStr =
                        timer.getAttribute(
                            "data-date"
                        );


                    const fid =
                        timer.getAttribute(
                            "data-id"
                        );


                    const targetDate =
                        new Date(
                            targetDateStr
                        ).getTime();


                    const distance =
                        targetDate - now;


                    const container =
                        timer.closest(
                            ".countdown-badge-container"
                        );


                    if (distance < 0) {

                        if (container) {

                            container.innerHTML = `

                                <div
                                    style="
                                        background:#25D366;
                                        color:white;
                                        font-size:10px;
                                        font-weight:800;
                                        text-align:center;
                                        border-radius:8px;
                                        padding:5px;
                                    ">

                                    ✨ FESTIVAL IS LIVE NOW!

                                </div>

                            `;

                        }

                        return;

                    }


                    const d =
                        Math.floor(
                            distance /
                            (1000 * 60 * 60 * 24)
                        );


                    const h =
                        Math.floor(
                            (
                                distance %
                                (1000 * 60 * 60 * 24)
                            ) /
                            (1000 * 60 * 60)
                        );


                    const m =
                        Math.floor(
                            (
                                distance %
                                (1000 * 60 * 60)
                            ) /
                            (1000 * 60)
                        );


                    const s =
                        Math.floor(
                            (
                                distance %
                                (1000 * 60)
                            ) /
                            1000
                        );


                    const days =
                        document.getElementById(
                            `days-${fid}`
                        );


                    const hours =
                        document.getElementById(
                            `hours-${fid}`
                        );


                    const minutes =
                        document.getElementById(
                            `minutes-${fid}`
                        );


                    const seconds =
                        document.getElementById(
                            `seconds-${fid}`
                        );


                    if (days) {

                        days.innerText =
                            d < 10
                            ? "0" + d
                            : d;

                    }


                    if (hours) {

                        hours.innerText =
                            h < 10
                            ? "0" + h
                            : h;

                    }


                    if (minutes) {

                        minutes.innerText =
                            m < 10
                            ? "0" + m
                            : m;

                    }


                    if (seconds) {

                        seconds.innerText =
                            s < 10
                            ? "0" + s
                            : s;

                    }

                });

        }


        updateAllTimers();


        setInterval(
            updateAllTimers,
            1000
        );

    }
);



/* =====================================================
   DARK MODE
===================================================== */

function toggleTheme() {

    const body =
        document.body;

    const icon =
        document.getElementById(
            "theme-icon"
        );


    body.classList.toggle(
        "dark-mode"
    );


    const isDark =
        body.classList.contains(
            "dark-mode"
        );


    icon.innerText =
        isDark
        ? "☀️"
        : "🌙";


    localStorage.setItem(
        "user-theme",
        isDark
        ? "dark"
        : "light"
    );

}



/* =====================================================
   LOAD SAVED THEME
===================================================== */

window.addEventListener(
    "DOMContentLoaded",
    function() {

        const savedTheme =
            localStorage.getItem(
                "user-theme"
            );


        const icon =
            document.getElementById(
                "theme-icon"
            );


        if (
            savedTheme === "dark"
        ) {

            document.body.classList.add(
                "dark-mode"
            );


            icon.innerText =
                "☀️";

        }

    }
);



/* =====================================================
   MOBILE ACTIVITY FEED
===================================================== */

function adjustFeedForMobile() {

    if (window.innerWidth < 768) {

        document
            .querySelectorAll(
                ".activity-name"
            )
            .forEach(function(el) {

                if (
                    el.innerText.length > 18
                ) {

                    el.style.fontSize =
                        "12px";

                }

            });

    }

}


window.addEventListener(
    "resize",
    adjustFeedForMobile
);


adjustFeedForMobile();



