export interface LoginUser {
  access_token: string;
  access_token_expiration: string;
  refresh_token_expiration: string;
  user: {
    pk: number;
    username: string;
    email: string ;
    first_name: string ;
    last_name: string ;
  },
}
