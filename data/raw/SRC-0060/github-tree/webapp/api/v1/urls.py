from django.urls import include, path

urlpatterns = [
  path("health-check/", include("api.v1.health_check.urls")),
  path("users/", include("api.v1.users.urls")),
  path("", include("api.v1.companies.urls")),
  path("", include("api.v1.stocks.urls")),
  path("", include("api.v1.financial_statements.urls")),
  path("", include("api.v1.disclosures.urls")),
  path("", include("api.v1.watchlists.urls")),
]
