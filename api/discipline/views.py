from fastapi import APIRouter, HTTPException, Query

from models.app_models import Discipline, DisciplineDTO, LessonDTO, Lesson

router = APIRouter()


@router.get('s')
async def get_disciplines():
    try:
        # Fetching all disciplines with their related lessons
        disciplines = await Discipline.all().prefetch_related("lessons")

        # Construct a list of disciplines with their details and associated lessons
        disciplines_data = [{
            "id": discipline.id,
            "name": discipline.name,
            "description": discipline.description,
            "lessons": [
                {"id": lesson.id, "name": lesson.name, "type_of_lesson": lesson.type_of_lesson,
                 "number": lesson.lesson_number}
                for lesson in discipline.lessons
            ]
        } for discipline in disciplines]

        if disciplines_data:
            return disciplines_data
        else:
            return {"message": "No disciplines available"}
    except Exception as e:
        # Handling any unexpected exceptions
        return {"message": str(e)}


@router.get('/{discipline_id}')
async def get_discipline(discipline_id: int = None):
    try:
        discipline = await Discipline.get(id=discipline_id).prefetch_related("lessons")
        return {
            "id": discipline.id,
            "name": discipline.name,
            "description": discipline.description,
            "lessons": [{"name": lesson.name, "type": lesson.type_of_lesson, "number": lesson.lesson_number} for lesson
                        in discipline.lessons]
        }
    except Exception as e:
        return {"message": str(e)}


@router.get('/{discipline_id}/lessons')
async def get_lessons(discipline_id: int = None):
    try:
        # import ipdb; ipdb.set_trace()

        discipline = await Discipline.get(id=discipline_id).prefetch_related("lessons")
        return discipline.lessons.related_objects
    except Exception as e:
        return {"message": e}


@router.post('')
async def create_discipline(discipline: DisciplineDTO = None):
    try:
        new_discipline = await Discipline.create(
            name=discipline.name,
            description=discipline.description
        )
        # Assuming Discipline model has a method to fetch associated lessons
        # This could be a method like new_discipline.get_lessons() if you're using an ORM
        lessons = await new_discipline.get_lessons() if hasattr(new_discipline, 'get_lessons') else []
        return {
            "id": new_discipline.id,
            "name": new_discipline.name,
            "description": new_discipline.description,
            "lessons": lessons  # Assuming lessons are serialized to a list of dicts
        }
    except Exception as e:
        return {"message": str(e)}, 400  # Include proper HTTP status code on errors


@router.post('/{discipline_id}/lessons')
async def create_lesson_discipline(discipline_id: int = None, lesson: LessonDTO = None):
    try:
        discipline = await Discipline.get_or_none(id=discipline_id)
        if not discipline:
            raise HTTPException(status_code=404, detail="Discipline not found")

        lesson = await Lesson.create(
            name=lesson.name,
            type_of_lesson=lesson.type_of_lesson,
            lesson_number=lesson.lesson_number,
            discipline=discipline
        )
        return lesson
    except Exception as e:
        return {"message": str(e)}


@router.delete('/{discipline_id}/lessons/{lesson_id}')
async def delete_lesson_discipline(discipline_id: int = None, lesson_id: int = None):
    try:
        discipline = await Discipline.get_or_none(id=discipline_id)
        if not discipline:
            raise HTTPException(status_code=404, detail="Discipline not found")

        lesson = await Lesson.get(id=lesson_id, discipline=discipline)
        await lesson.delete()
        return {"message": "Lesson for discipline deleted successfully"}
    except Exception as e:
        return {"message": e}


@router.delete('/{discipline_id}')
async def delete_discipline(discipline_id: int = None):
    try:
        discipline = await Discipline.get(id=discipline_id)
        await discipline.delete()
        return {"message": "Discipline deleted successfully"}
    except Exception as e:
        return {"message": e}


@router.get('s/by_letter')
async def get_disciplines_by_letter(start_letter: str = Query(..., min_length=1, max_length=1, description="First letter of the discipline name")):
    try:
        # Ensuring the letter is uppercase for consistency
        start_letter = start_letter.upper()

        # Fetching disciplines that start with the given letter
        disciplines = await Discipline.filter(name__istartswith=start_letter).prefetch_related("lessons")

        # Constructing the response with discipline details
        disciplines_data = [{
            "id": discipline.id,
            "name": discipline.name,
            "description": discipline.description,
            "lessons": [
                {"id": lesson.id, "name": lesson.name, "type_of_lesson": lesson.type_of_lesson, "number": lesson.lesson_number}
                for lesson in discipline.lessons
            ]
        } for discipline in disciplines]

        if disciplines_data:
            return disciplines_data
        else:
            return []
    except Exception as e:
        # Handling any unexpected exceptions
        return {"message": str(e)}, 400