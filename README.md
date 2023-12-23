
# Projeto Integrador API - Documentação das Rotas

## Questions

### GET /questions - Listar Todas as Perguntas

-   **Response (JSON)**

      ```json
    [
      {
        "title": "Título da pergunta",
        "description": "Descrição da pergunta",
        "author_name": "Nome do Autor",
        "author_profile_picture": "URL da imagem de perfil"
      }
      // ... mais perguntas
    ]
### GET /questions/search - Buscar Perguntas por Título

-   **Query Params**: `title`
-   **Response (JSON)**
    
     ```json
    [
      {
        "id": 1,
        "title": "Título da pergunta",
        "description": "Descrição da pergunta",
        "author_name": "Nome do Autor",
        "author_profile_picture": "URL da imagem de perfil"
      }
      // ... mais perguntas
    ] 
### POST /questions - Adicionar Pergunta

*- **Require JWT Token***
-   **Body (JSON)**
     ```json
    {
      "title": "Título da pergunta",
      "description": "Descrição da pergunta"
    }
    
-   **Response (JSON)**
    
    `{"message": "Question added successfully"}` 
    
### PUT /questions/int:question_id - Atualizar Pergunta

*- **Require JWT Token***
-   **Body (JSON)**
     ```json
    `{
      "title": "Novo título",
      "description": "Nova descrição"
    }` 
-   **Response (JSON)**
    
    `{"message": "Question updated successfully"}` 
    

### DELETE /questions/int:question_id - Deletar Pergunta

*- **Require JWT Token***
-   **Response (JSON)**
    
    `{"message": "Question deleted successfully"}` 
    

### POST /questions/int:question_id/like - Dar Like em Pergunta

*- **Require JWT Token***
-   **Response (JSON)**
 
    `{"message": "Liked question successfully"}` 
    

### POST /questions/int:question_id/dislike - Dar Dislike em Pergunta

*- **Require JWT Token***
-   **Response (JSON)**
- 
    `{"message": "Disliked question successfully"}` 
    

## Comments

### GET /questions/int:question_id/comments - Listar Comentários de uma Pergunta

-   **Response (JSON)**
    
    ```json
    `[
      {
        "content": "Conteúdo do comentário",
        "author_name": "Nome do Autor",
        "author_profile_picture": "URL da imagem de perfil"
      }
      // ... mais comentários
    ]` 
### POST /questions/int:question_id/comments - Adicionar Comentário

*- **Require JWT Token***
-   **Body (JSON)**

    ```json
    `{
      "content": "Conteúdo do comentário"
    }` 
-   **Response (JSON)**
        
    `{"message": "Comment added successfully"}` 
    

### PUT /comments/int:comment_id - Atualizar Comentário

*- **Require JWT Token***
-   **Body (JSON)**
    ```json
    `{
      "content": "Novo conteúdo do comentário"
    }` 
-   **Response (JSON)**
    
    `{"message": "Comment updated successfully"}` 
    

### DELETE /comments/int:comment_id - Deletar Comentário

*- **Require JWT Token***
-   **Response (JSON)**
       
    `{"message": "Comment deleted successfully"}` 
    

### POST /comments/int:comment_id/like - Dar Like em Comentário

*- **Require JWT Token***
-   **Response (JSON)**
        
    `{"message": "Liked comment successfully"}` 
    

### POST /comments/int:comment_id/dislike - Dar Dislike em Comentário

*- **Require JWT Token***
-   **Response (JSON)**
        
    `{"message": "Disliked comment successfully"}` 
    

## Users

### GET /user/int:user_id/history - Histórico de Perguntas do Usuário

*- **Require JWT Token***
-   **Response (JSON)**
   
    ```json
    `[
      {
        "title": "Título da pergunta",
        "description": "Descrição da pergunta"
      }
      // ... mais perguntas
    ]` 
### GET /user/int:user_id/bookmarks - Listar Bookmarks de Usuário

*- **Require JWT Token***
-   **Response (JSON)**
   
    ```json
    `[
      {
        "question_id": 1,
        "title": "Título da pergunta",
        "description": "Descrição da pergunta"
      }
      // ... mais bookmarks
    ]` 
### POST /register - Registrar Usuário

-   **Body (JSON)**
    ```json
    `{
      "email": "email@exemplo.com",
      "name": "Nome do Usuário",
      "age": 30,
      "password": "senha",
      "confirm_password": "senha"
    }` 
-   **Response (JSON)**
    
    `{"message": "User registered successfully"}` 
    

### POST /login - Login de Usuário

-   **Body (JSON)**

    ```json
    `{
      "email": "email@exemplo.com",
      "password": "senha"
    }`     
-   **Response (JSON)**
  
    `{"access_token": "token_jwt"}` 
    

### PUT /user/int:user_id - Atualizar Usuário

*- **Require JWT Token***
-   **Body (JSON)**
    
    
    `{
      "name": "Novo Nome",
      "age": 31,
      "password": "nova senha"
    }` 
    
-   **Response (JSON)**
    
    
    `{"message": "User updated successfully"}` 
    

### DELETE /user/int:user_id/bookmark/int:question_id - Remover Bookmark

*- **Require JWT Token***
-   **Response (JSON)**
    
    `{"message": "Bookmark removed successfully"}` 
    

### POST /user/int:user_id/bookmark/int:question_id - Adicionar Bookmark

*- **Require JWT Token***

-   **Response (JSON)**
   
    
    `{"message": "Bookmark added successfully"}` 
    

### POST /upload/int:user_id - Upload de Imagem de Perfil

*- **Require JWT Token***

-   **Body**: FormData com arquivo 'file'
-   **Response (JSON)**
    
    `{"message": "File uploaded successfully"}`
