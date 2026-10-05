// Copyright (c) 2026 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
//
// This work is licensed under the terms of the MIT license.
// For a copy, see <https://opensource.org/licenses/MIT>.

#include "carla/multigpu/listener.h"
#include "carla/multigpu/primary.h"

#include "carla/Logging.h"

#include <boost/asio/post.hpp>

#include <memory>

namespace carla {
namespace multigpu {

  Listener::Listener(boost::asio::io_context &io_context, endpoint ep)
    : _io_context(io_context),
      _acceptor(_io_context, std::move(ep)),
      _timeout(time_duration::seconds(1u)) {
        _acceptor.listen();
      }

  Listener::~Listener() {
    Stop();
  }
  
  void Listener::Stop() {
    std::lock_guard<std::mutex> lock(_acceptor_mutex);
    if (_stopped.exchange(true)) {
      return;
    }
    boost::system::error_code ec;
    _acceptor.cancel(ec);
    _acceptor.close(ec);
    _io_context.stop();
  }
  
  void Listener::OpenSession(
      time_duration timeout,
      callback_function_type on_opened,
      callback_function_type on_closed,
      callback_function_type_response on_response) {

    using boost::system::error_code;

    std::lock_guard<std::mutex> lock(_acceptor_mutex);
    if (_stopped) {
      return;
    }

    auto session = std::make_shared<Primary>(_io_context, timeout, *this);
    auto self = shared_from_this();
    
    auto handle_query = [on_opened, on_closed, on_response, session, self](const error_code &ec)
    {
      if (self->_stopped) {
        return;
      }
      if (!ec) {
        session->Open(std::move(on_opened), std::move(on_closed), std::move(on_response));
      } else {
        log_error("Secondary server:", ec.message());
      }
    };

    _acceptor.async_accept(
      session->_socket,
      [self, handle_query, timeout, on_opened, on_closed, on_response](error_code ec)
      {
        if (self->_stopped) {
          return;
        }
        boost::asio::post(
          self->_io_context,
          [ec, handle_query]()
          {
            handle_query(ec);
          });

        self->OpenSession(timeout, on_opened, on_closed, on_response);
      });
  }

} // namespace multigpu
} // namespace carla
