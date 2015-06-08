from pyramid.security import Allow, Everyone, Deny

from pyramid_web20.system import admin


@admin.ModelAdmin.register(model='websauna.referral.models.ReferralProgram')
class ReferralProgramAdmin(admin.ModelAdmin):

    #: Traverse id
    id = "referrals"

    #: Traverse title
    title = "Referral Programs"

    singular_name = "referral program"
    plural_name = "referral programs"

    class Resource(admin.ModelAdmin.Resource):
        """Present one shortener URL in admin traversing hierarchy."""



