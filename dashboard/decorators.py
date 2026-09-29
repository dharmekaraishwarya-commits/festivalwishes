from django.shortcuts import redirect


def admin_login_required(view_function):


    def wrapper(request, *args, **kwargs):


        admin_id = request.session.get(
            "admin_id"
        )


        if not admin_id:

            return redirect(
                "dashboard:login"
            )


        return view_function(

            request,

            *args,

            **kwargs

        )


    return wrapper