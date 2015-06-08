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
        pass



@admin.ModelAdmin.register(model='websauna.referral.models.Conversion')
class ConversionAdmin(admin.ModelAdmin):

    # Conversionsshould not have web exposed edits
    __acl__ = [
        (Deny, Everyone, 'add'),
        (Deny, Everyone, 'edit'),
    ]

    #: Traverse id
    id = "conversions"

    #: Traverse title
    title = "Referral Conversions"

    singular_name = "conversion"
    plural_name = "conversions"

    class Resource(admin.ModelAdmin.Resource):
        pass
