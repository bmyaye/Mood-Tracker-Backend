from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated

from .. import deps
from .. import models

router = APIRouter(prefix="/users", tags=["users"])

<<<<<<< Updated upstream
=======
# Create User
@router.post("/")
async def create_user(
    user: RegisteredUser,
    session: AsyncSession = Depends(get_session)
    )->  models.User:
    query = select(DBUser).where(DBUser.username == user.username)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_user = DBUser(**user.dict())
    await db_user.set_password(user.password)  # Encrypt password before saving
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    # Create a Point for user



    await session.commit()  # Commit the Point to generate the point_id

    return db_user
>>>>>>> Stashed changes

@router.get("/me")
async def get_me(
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:
    return current_user


# @router.get("/{user_id}")
# async def get(
#     user_id: str,
#     session: Annotated[AsyncSession, Depends(models.get_session)],
# ) -> models.User:
#     user = await session.get(models.DBUser, user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Not found this user",
#         )
#     return user


@router.post("/create_account")
async def create(
    user_info: models.RegisteredUser,
    session: Annotated[AsyncSession, Depends(models.get_session)]
) -> models.DBUser:
    # Check if username exists
    result = await session.execute(
        select(models.DBUser).where(models.DBUser.username == user_info.username)
    )
    user = result.scalar_one_or_none()
    
    print("Attempting to create user with username:", user_info.username)  # Debug: Print username being checked
    print("Existing user found:", user)  # Debug: Print existing user if found

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username already exists.",
        )

    # Create new user
    user = models.DBUser.from_orm(user_info)
    await user.set_password(user_info.password)
    session.add(user)
    await session.commit()

    return user

@router.put("/{user_id}/change_password")
async def change_password(
    user_id: str,
    password_update: models.ChangedPassword,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:
    # Get the user by user_id
    user = await session.get(models.DBUser, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Debug: Print the stored hashed password and the provided password
    print("Stored password hash:", user.hashed_password)  # Debugging: Print the stored hashed password
    print("Current password:", password_update.current_password)  # Debugging: Print the current password from request
    print("Password match:", user.verify_password(password_update.current_password))  # Debugging: Check if passwords match

    # Verify the current password
    if not user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    # Set new password and save changes
    await user.set_password(password_update.new_password)
    session.add(user)
    await session.commit()

    return {"msg": "Password updated successfully"}


@router.put("/{user_id}/update_data")
async def update(
    user_id: int,
    user_update: models.UpdatedUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:

    db_user = await session.get(models.DBUser, user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )
    
    if not db_user.verify_password(user_update.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    db_user.sqlmodel_update(user_update)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.delete("/{user_id}/delete_account")
async def delete(
    user_id: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:

    user = await session.get(models.DBUser, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    session.delete(user)
    await session.commit()

    return {"message": "User deleted successfully."}