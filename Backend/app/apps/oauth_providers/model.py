


# class OAuth2Token(Model):
#     name = String(length=40)
#     token_type = String(length=40)
#     access_token = String(length=200)
#     refresh_token = String(length=200)
#     expires_at = PositiveIntegerField()
#     user = ForeignKey(User)
#
#     def to_token(self):
#         return dict(
#             access_token=self.access_token,
#             token_type=self.token_type,
#             refresh_token=self.refresh_token,
#             expires_at=self.expires_at
#         )


# for auto update_token
# def update_token(name, token, refresh_token=None, access_token=None):
#     if refresh_token:
#         item = OAuth2Token.find(name=name, refresh_token=refresh_token)
#     elif access_token:
#         item = OAuth2Token.find(name=name, access_token=access_token)
#     else:
#         return
#
#     # update old token
#     item.access_token = token['access_token']
#     item.refresh_token = token.get('refresh_token')
#     item.expires_at = token['expires_at']
#     item.save()



