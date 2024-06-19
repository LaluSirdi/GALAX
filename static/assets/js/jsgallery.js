function postDetail(itemId, type) {
    $.ajax({
        url: '/postDetail/' + type + '/' + itemId,
        type: 'GET',
        success: function(response) {
            $('#_id').val(itemId);
            $('#nama').text(response.nama);
            $('#type').val(type);
            $('#deskripsi').text(response.deskripsi);
            $('#postDetailForm').attr('action', '/postDetail/' + type + '/' + itemId);
            if (response.gambar) {
                $('#gambar').attr('src', '/static/assets/img/gallery/' + type + '/' + response.gambar);
            }
        },
        error: function(error) {
            console.log(error);
        }
    });
}

$(document).on('click', '#comment-btn', function(e) {
  e.preventDefault();
  const itemId = $(this).data('id');
  const type = $(this).data('type');

      alert('Item ID atau tipe tidak valid.');

});

function submitComment() {
    var formData = $('#postDetailForm').serialize();
    $.ajax({
        url: $('#postDetailForm').attr('action'),
        type: 'POST',
        data: formData,
        success: function(response) {
            location.reload();
        },
        error: function(error) {
            console.log(error);
        }
    });
}

function formatCommentDate(commentDate) {
  let now = new Date();
  let date = new Date(commentDate);
  let diff = now - date;
  
  if (diff < 60000) {
      return 'Baru saja';
  } else if (diff < 3600000) {
      let minutes = Math.floor(diff / 60000);
      return `${minutes} menit yang lalu`;
  } else if (diff < 86400000) {
      let hours = Math.floor(diff / 3600000);
      return `${hours} jam yang lalu`;
  } else if (diff < 604800000) { 
      let days = Math.floor(diff / 86400000);
      return `${days} hari yang lalu`;
  } else {
      return date.toLocaleDateString('id-ID', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
      });
  }
}

function sendReply(commentId, replyText) {
$.ajax({
    url: '/add_reply',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        comment_id: commentId,
        reply: replyText
    }),
    success: function(response) {
        if (response.success) {
            loadComments($('#galleryId').val());
            location.reload();
        } else {
            console.error('Error adding reply:', response.error);
        }
    },
    error: function(xhr, status, error) {
        console.error('Error adding reply:', error);
    }
});
}

function loadComments(id_gallery) {
console.log(`Fetching comments for gallery ID: ${id_gallery}`);

$.ajax({
    url: '/comments/' + id_gallery,
    type: 'GET',
    dataType: 'json',
    success: function(response) {
        console.log(response);
        let comments = response.comments;
        let activeUser = response.active_user;
        let commentSection = $('#commentSection');
        commentSection.empty();

        if (comments.length === 0) {
            commentSection.append('<p>No comments available.</p>');
        } else {
            comments.forEach(comment => {
                console.log(`Comment: ${comment.comment}, User: ${comment.username}, Date: ${comment.tanggal}`);

                let formattedDate = formatCommentDate(comment.tanggal);
                let editDeleteActions = '';

                if (comment.username === activeUser) {
                    editDeleteActions = `
                        <span class="edit" data-id="${comment._id}"><img src="https://img.icons8.com/?size=23&id=11762&format=png&color=000000" /></span>
                        <span class="delete" data-id="${comment._id}"><img src="https://img.icons8.com/?size=23&id=89287&format=png&color=000000" /></span>
                    `;
                }

                let likesImgSrc = 'https://img.icons8.com/?size=20&id=89385&format=png&color=000000';
                if (comment.likes > 0 && comment.liked_by_active_user) {
                    likesImgSrc = 'https://img.icons8.com/?size=20&id=85597&format=png&color=000000';
                }

                let repliesHtml = '';
                if (comment.replies && comment.replies.length > 0) {
                    let showRepliesText = comment.replies.length > 0 ? `Lihat ${comment.replies.length} balasan lainnya` : 'Tutup balasan';
                    repliesHtml += `
                        <span class="show-replies" data-id="${comment._id}">
                            ${showRepliesText}
                        </span>
                        <div class="replies" style="display:none;">
                    `;
                    comment.replies.forEach((reply, index) => {
                      let editDeleteActionsR = '';

                      if (reply.username === activeUser) {
                          editDeleteActionsR = `
                              <span class="editR" data-comment-id="${comment._id}" data-reply-index="${index}"><img src="https://img.icons8.com/?size=20&id=11762&format=png&color=000000" /></span>
                              <span class="deleteR" data-comment-id="${comment._id}" data-reply-index="${index}"><img src="https://img.icons8.com/?size=20&id=89287&format=png&color=000000" /></span>
                          `;
                      }
                      let likesImgSrc = 'https://img.icons8.com/?size=20&id=89385&format=png&color=000000';
                      if (reply.likes > 0 && reply.liked_by_active_user) {
                          likesImgSrc = 'https://img.icons8.com/?size=20&id=85597&format=png&color=000000';
                      }
                      repliesHtml += `
                          <div class="reply" data-comment-id="${comment._id}" data-reply-index="${index}">
                                <div class="comment-avatar">
                                    <img src="../static/assets/img/profile_pics/${reply.image}" alt="Avatar" />
                                </div>
                                <div class="comment-content">
                                    <h6>${reply.username}</h6>
                                    <span class="comment-date">${formatCommentDate(reply.tanggal)}</span>
                                    <p id="creply">${reply.comment}</p>
                                    <textarea class="edit-reply-input" style="display:none;"></textarea>
                                    <div class="comment-actions">
                                        <span class="likes mb-0" id="like" data-comment-id="${comment._id}" data-reply-index="${index}">
                                            <img src="${likesImgSrc}" /> ${reply.likes}
                                        </span>
                                        <p class="ml-auto mb-0">
                                          ${editDeleteActionsR}
                                        </p>
                                    </div>
                                </div>
                          </div>`;
                    });
                    repliesHtml += '</div>';
                }

                let commentDiv = `
                    <div class="comment" data-id="${comment._id}">
                        <div class="comment-avatar">
                            <img src="../static/assets/img/profile_pics/${comment.image}" alt="Avatar" />
                        </div>
                        <div class="comment-content">
                            <input type="hidden" id="galleryId" name="galleryId" value="">
                            <h6 id="id_user">${comment.username}</h6>
                            <span class="comment-date">${formattedDate}</span>
                            <p id="comment">${comment.comment}</p><br>
                            <textarea class="edit-comment-input" style="display:none;"></textarea>
                            <textarea class="reply-comment-input" style="display:none;"></textarea>
                            <div class="comment-actions">
                                <span class="likes mb-0 like-comment" data-id="${comment._id}">
                                    <img src="${likesImgSrc}" /> ${comment.likes}
                                </span>
                                <span class="btn-reply" data-id="${comment._id}">Balas</span>
                                <p class="ml-auto mb-0">
                                    ${editDeleteActions}
                                </p>
                            </div>
                            ${repliesHtml}
                            <div class="reply-section" style="display:none;">
                                <textarea class="reply-input" placeholder="Tulis balasan Anda"></textarea>
                                <button class="send-reply" data-id="${comment._id}">Kirim</button>
                            </div>
                        </div>
                    </div>`;
                commentSection.append(commentDiv);
            });

            $(document).on('click', '.show-replies', function() {
              let commentId = $(this).data('id');
              let repliesSection = $(`div.comment[data-id="${commentId}"] .replies`);
              let showRepliesSpan = $(this);
          
              repliesSection.toggle();
              if (repliesSection.is(':visible')) {
                  showRepliesSpan.text('Tutup balasan');
              } else {
                  let repliesCount = $(`div.comment[data-id="${commentId}"] .reply`).length;
                  let showRepliesText = repliesCount > 0 ? `Lihat ${repliesCount} balasan lainnya` : 'Lihat balasan';
                  showRepliesSpan.text(showRepliesText);
              }
            });              

            $('.btn-reply').click(function() {
              let commentId = $(this).data('id');
              let replySection = $(`div.comment[data-id="${commentId}"] .reply-section`);
              replySection.toggle();
            });

            $('.send-reply').click(function() {
                let commentId = $(this).data('id');
                let replyInput = $(`div.comment[data-id="${commentId}"] .reply-input`);
                let replyText = replyInput.val();
                if (replyText.trim()) {
                    sendReply(commentId, replyText);
                }
            });

            $('.edit').click(function() {
              let commentId = $(this).data('id');
              let commentDiv = $(`div.comment[data-id="${commentId}"]`);
              let commentText = commentDiv.find('p#comment');
              let editInput = commentDiv.find('.edit-comment-input');
              let editButton = $(this);

              commentText.hide();
              editInput.show().val(commentText.text()).focus();

              editInput.off('blur').on('blur', function() {
                  let newComment = editInput.val();
                  updateComment(commentId, newComment, commentText, editInput, editButton);
              });

              editInput.off('keypress').on('keypress', function(e) {
                  if (e.which === 13) { 
                      e.preventDefault(); 
                      let newComment = editInput.val();
                      updateComment(commentId, newComment, commentText, editInput, editButton);
                  }
              });
            });

            $('.delete').click(function() {
                let commentId = $(this).data('id');
                deleteComment(commentId);
            });

            commentSection.on('click', '.like-comment', function() {
              let commentId = $(this).data('id');
              likeComment(commentId);
            });

            $(document).on('click', '.editR', function() {
              let commentId = $(this).data('comment-id');
              let replyIndex = $(this).data('reply-index');
              let replyDiv = $(`div.comment[data-id="${commentId}"] .reply[data-reply-index="${replyIndex}"]`);
              let replyText = replyDiv.find('p');
              let editInput1 = replyDiv.find('.edit-reply-input');
          
              replyText.hide();
              editInput1.show().val(replyText.text()).focus();
          
              editInput1.off('blur').off('keypress');
          
              editInput1.on('blur', function() {
                  let newReply = editInput1.val();
                  updateReply(commentId, replyIndex, newReply, replyText, editInput1);
              });
          
              editInput1.on('keypress', function(e) {
                  if (e.which === 13) { 
                      e.preventDefault();
                      let newReply = editInput1.val();
                      updateReply(commentId, replyIndex, newReply, replyText, editInput1);
                  }
              });
            });              

            $('.deleteR').click(function() {
              let commentId = $(this).data('comment-id');
              let replyIndex = $(this).data('reply-index');
              deleteReply(commentId, replyIndex);
            });

            commentSection.on('click', '#like', function() {
              let commentId = $(this).data('comment-id');
              let replyIndex = $(this).data('reply-index');
              likeReply(commentId, replyIndex);
            });
        }

        $('#galleryId').val(id_gallery);

        $('#commentsModal').modal('show');
    },
    error: function(xhr, status, error) {
        console.error('Error fetching comments:', error);
    }
});
}

function updateReply(commentId, replyIndex, newReply, replyText, editInput1) {
$.ajax({
    url: '/update_reply',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        comment_id: commentId,
        reply_index: replyIndex,
        new_reply: newReply
    }),
    success: function(response) {
        if (response.success) {
            replyText.text(newReply);
            replyText.show();
            editInput1.hide();
            loadComments($('#galleryId').val());
            location.reload();
        } else {
            console.error('Error updating reply:', response.error);
        }
    },
    error: function(xhr, status, error) {
        console.error('Error updating reply:', error);
    }
});
}

function deleteReply(commentId, replyIndex) {
$.ajax({
    url: '/delete_reply',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        comment_id: commentId,
        reply_index: replyIndex
    }),
    success: function(response) {
        if (response.success) {
            $(`div.comment[data-id="${commentId}"] .reply[data-reply-index="${replyIndex}"]`).remove();
            loadComments($('#galleryId').val());
            location.reload();
        } else {
            console.error('Error deleting reply:', response.error);
        }
    },
    error: function(xhr, status, error) {
        console.error('Error deleting reply:', error);
    }
});
}

function updateComment(commentId, newComment, commentText, editInput) {
$.ajax({
    url: '/update_comment',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        comment_id: commentId,
        new_comment: newComment
    }),
    success: function(response) {
        if (response.success) {
            commentText.text(newComment);
            commentText.show();
            editInput.hide();
        } else {
            console.error('Error updating comment:', response.error);
        }
    },
    error: function(xhr, status, error) {
        console.error('Error updating comment:', error);
    }
});
}

function deleteComment(commentId) {
$.ajax({
    url: '/delete_comment',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        comment_id: commentId
    }),
    success: function(response) {
        if (response.success) {
            $(`div.comment[data-id="${commentId}"]`).remove();
            location.reload();
        } else {
            console.error('Error deleting comment:', response.error);
        }
    },
    error: function(xhr, status, error) {
        console.error('Error deleting comment:', error);
    }
});
}

function likeReply(commentId, replyIndex) {
$.ajax({
    url: '/update_likes_reply',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        comment_id: commentId,
        reply_index: replyIndex
    }),
    success: function(response) {
        if (response.success) {
            let updatedReply = response.reply;
            let likesSpan = $(`.reply[data-comment-id="${commentId}"][data-reply-index="${replyIndex}"] .likes`);

            if (response.liked) {
                likesSpan.addClass('liked');
                likesSpan.html(`<img src="https://img.icons8.com/?size=20&id=85597&format=png&color=000000" /> ${updatedReply.likes}`);
            } else {
                likesSpan.removeClass('liked');
                likesSpan.html(`<img src="https://img.icons8.com/?size=20&id=89385&format=png&color=000000" /> ${updatedReply.likes}`);
            }
        } else {
            console.error('Error liking reply:', response.error);
        }
    },
    error: function(xhr, status, error) {
        console.error('Error liking reply:', error);
    }
});
}

function likeComment(commentId) {
$.ajax({
    url: '/update_likes',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
        comment_id: commentId
    }),
    success: function(response) {
        if (response.success) {
            let updatedComment = response.comment;
            let likesSpan = $(`.likes[data-id="${commentId}"]`);
            if (response.liked) {
                likesSpan.addClass('liked');
                likesSpan.html(`<img src="https://img.icons8.com/?size=20&id=85597&format=png&color=000000" /> ${updatedComment.likes}`);
            } else {
                likesSpan.removeClass('liked');
                likesSpan.html(`<img src="https://img.icons8.com/?size=20&id=89385&format=png&color=000000" /> ${updatedComment.likes}`);
            }
        } else {
            console.error('Error liking comment:', response.error);
        }
    },
    error: function(xhr, status, error) {
        console.error('Error liking comment:', error);
    }
});
}