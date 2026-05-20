"""Verification script to test authentication and role-based access control endpoints."""

import os
import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def main() -> None:
    """Run verification tests against the local running backend."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        print("1. Attempting login for Admin (thilina.fernando9@gmail.com)...")
        admin_login_res = await client.post(
            "/api/auth/login",
            json={
                "email": "thilina.fernando9@gmail.com",
                "password": os.getenv("ADMIN_SEED_PASSWORD", "mtsf1234"),
            },
        )
        if admin_login_res.status_code != 200:
            print(f"❌ Admin login failed: {admin_login_res.status_code}")
            print(admin_login_res.text)
            return

        admin_data = admin_login_res.json()
        print("✅ Admin login successful!")
        print(f"   Token Type: {admin_data.get('token_type')}")
        print(f"   User Email: {admin_data.get('user', {}).get('email')}")
        print(
            f"   Is Admin?   {admin_data.get('user', {}).get('is_admin')} (Expected: True)"
        )
        print(
            f"   Display:    {admin_data.get('user', {}).get('display_name')} (Expected: Thilina Fernando)"
        )

        admin_token = admin_data.get("access_token")

        print(
            "\n2. Attempting login for Player (sathira2000@gmail.com)..."
        )
        player_login_res = await client.post(
            "/api/auth/login",
            json={
                "email": "sathira2000@gmail.com",
                "password": os.getenv("RANSIKA_SEED_PASSWORD", "RansikaPlayer2026!"),
            },
        )
        if player_login_res.status_code != 200:
            print(f"❌ Player login failed: {player_login_res.status_code}")
            print(player_login_res.text)
            return

        player_data = player_login_res.json()
        print("✅ Player login successful!")
        print(f"   User Email: {player_data.get('user', {}).get('email')}")
        print(
            f"   Is Admin?   {player_data.get('user', {}).get('is_admin')} (Expected: False)"
        )
        print(
            f"   Display:    {player_data.get('user', {}).get('display_name')} (Expected: Ransika Bellanage)"
        )

        player_token = player_data.get("access_token")

        print("\n3. Testing Admin route /credentials using Player token...")
        player_headers = {"Authorization": f"Bearer {player_token}"}
        player_cred_res = await client.get("/api/credentials", headers=player_headers)
        print(f"   Status Code: {player_cred_res.status_code} (Expected: 403)")
        if player_cred_res.status_code == 403:
            print("✅ Correctly rejected player access!")
        else:
            print("❌ Security vulnerability! Player was not rejected with 403.")

        print("\n4. Testing Admin route /credentials using Admin token...")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        admin_cred_res = await client.get("/api/credentials", headers=admin_headers)
        print(f"   Status Code: {admin_cred_res.status_code} (Expected: 200)")
        if admin_cred_res.status_code == 200:
            print("✅ Admin access verified successfully!")
            print(f"   Data: {admin_cred_res.json()}")
        else:
            print("❌ Admin was rejected or endpoint errored.")


if __name__ == "__main__":
    asyncio.run(main())
