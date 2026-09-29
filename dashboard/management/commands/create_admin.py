from django.core.management.base import BaseCommand

from dashboard.models import AdminUser


class Command(BaseCommand):

    help = "Create custom dashboard admin"


    def handle(self, *args, **kwargs):

        username = input(
            "Username: "
        ).strip()


        if AdminUser.objects.filter(
            username=username
        ).exists():

            self.stdout.write(

                self.style.ERROR(

                    "Username already exists."

                )

            )

            return


        password = input(
            "Password: "
        )


        confirm_password = input(
            "Confirm Password: "
        )


        if password != confirm_password:

            self.stdout.write(

                self.style.ERROR(

                    "Passwords do not match."

                )

            )

            return


        admin_user = AdminUser(

            username=username

        )


        admin_user.set_password(
            password
        )


        admin_user.save()


        self.stdout.write(

            self.style.SUCCESS(

                "Admin created successfully!"

            )

        )