from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from .models import Book
from .serializers import BookSerializer
from rest_framework.throttling import AnonRateThrottle
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import APIException, NotFound
from utils.encryption import decode_token
from django.shortcuts import get_object_or_404
# Create your views here.

# ... (imports)

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            name='page',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Page number for paginated response'
        ),
        openapi.Parameter(
            name='page_size',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='Number of books per page'
        )
    ],
    responses={
        200: 'Successful response',
        404: 'Not Found',
        500: 'Internal Server Error'
    }
)
@throttle_classes([AnonRateThrottle])
@api_view(["GET"])
def get_book_listing(request):
    try:
        paginator = CustomPagination()
        books = Book.objects.select_related("author").all()

        if not books.exists():
            raise NotFound("No books found")

        result_page = paginator.paginate_queryset(books, request)
        serialized_books = BookSerializer(result_page, many=True)

        return Response({"status": True, "data": serialized_books.data}, status=status.HTTP_200_OK)
   
    except NotFound as e:
        return Response({"status": False, "error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"status": False, "error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# GET Book By book_id
@swagger_auto_schema(
    methods=['GET'],
    operation_summary="Get Book by ID",
    responses={200: "Success", 404: "Not Found"},
    manual_parameters=[
        openapi.Parameter(
            name='book_id',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
            description='ID of the book to retrieve',
        ),
    ],
)
@api_view(['GET'])
def get_book_by_id(request, book_id):
    try:
        book = get_object_or_404(Book, id=book_id)
        serialized_book = BookSerializer(book)
        return Response({"status": True, "data": serialized_book.data}, status=status.HTTP_200_OK)
   
    except Exception as e:
        return Response({"status": False, "error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

# Create a new book
@swagger_auto_schema(
    method='post',
    manual_parameters=[
         openapi.Parameter(
            'auth-token',
            openapi.IN_HEADER,
            description="Token for authorization",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'ISBN': openapi.Schema(type=openapi.TYPE_STRING),
            'publication_date': openapi.Schema(type=openapi.TYPE_STRING)
        },
        required=[ 'title', 'ISBN']
    ),
    responses={
        201: 'Created',
        400: 'Bad Request',
        500: 'Internal Server Error'
    }
)
@throttle_classes([AnonRateThrottle])
@api_view(["POST"])
def create_book(request):
     try:
        token = request.headers.get('auth-token')
        if not token:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        payload = decode_token(token)  # Assuming you have a function to decode the token
        if isinstance(payload.get("id"), int):
            request_data = request.data.copy()
            request_data["author"] = payload["id"]
            new_book = BookSerializer(data=request_data)
            
            if new_book.is_valid():
                new_book.save()
                return Response({"status": True, "data": new_book.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"status": False, "error": new_book.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"status": False, "error": "Invalid user ID in token"}, status=status.HTTP_401_UNAUTHORIZED)
     except APIException as e:
        return Response({"status": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
     except Exception as e:
        return Response({"status": False, "error": "Internal Server Error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Update an existing Book
@swagger_auto_schema(
    method="put",
    manual_parameters=[
         openapi.Parameter(
            'auth-token',
            openapi.IN_HEADER,
            description="Token for authorization",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            name='book_id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='ID of the book to update'
        )
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'author': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['title']
    ),
    responses={
        200: 'Updated',
        404: 'Not Found',
        500: 'Internal Server Error'
    }
)
@api_view(["PUT"])
def update_book(request):
    try:
        book_id = request.query_params.get("book_id")
        
        if not book_id:
            raise NotFound("Book ID not provided")

        book_instance = Book.objects.filter(id=book_id).first()

        if not book_instance:
            raise NotFound("Book not found")

        updated_book = BookSerializer(book_instance, data=request.data, partial=True)
        updated_book.is_valid(raise_exception=True)
        updated_book.save()

        return Response({"status": True, "data": updated_book.data}, status=status.HTTP_200_OK)
    
    except NotFound as e:
        return Response({"status": False, "error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status": False, "error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Delete an existing book
@swagger_auto_schema(
    method="delete",
    manual_parameters=[
        openapi.Parameter(
            name='book_id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description='ID of the book to delete'
        )
    ],
    responses={
        200: 'Deleted',
        500: 'Internal Server Error'
    }
)
@throttle_classes([AnonRateThrottle])
@api_view(["DELETE"])
def delete_book(request):
    try:
        book_id = request.query_params.get("book_id")
        
        if not book_id:
            raise NotFound("Book ID not provided")

        book_instance = Book.objects.filter(id=book_id).first()

        if not book_instance:
            raise NotFound("Book not found")

        book_instance.delete()

        return Response({"status": True, "data": "Book deleted successfully"}, status=status.HTTP_200_OK)
    
    except NotFound as e:
        return Response({"status": False, "error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({"status": False, "error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
