// Copyright (c) 2026 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
// SPDX-License-Identifier: MIT

#include "test.h"
#include "carla/multigpu/listener.h"
#include "carla/multigpu/primary.h"

using carla::multigpu::Listener;
using carla::multigpu::Primary;

TEST(multigpu_shutdown, closed_socket_does_not_open_or_throw) {
  boost::asio::io_context io;
  auto listener = std::make_shared<Listener>(io,
      Listener::endpoint(boost::asio::ip::address_v4::loopback(), 0));
  auto session = std::make_shared<Primary>(io, carla::time_duration::seconds(1), *listener);
  int opened = 0;
  EXPECT_NO_THROW(session->Open([&](auto) { ++opened; },
      [](auto) {}, [](auto, carla::Buffer) {}));
  EXPECT_EQ(opened, 0);
}

TEST(multigpu_shutdown, canceled_completion_cannot_reopen_after_repeat_stop) {
  for (int attempt = 0; attempt < 100; ++attempt) {
    boost::asio::io_context io;
    auto listener = std::make_shared<Listener>(io,
        Listener::endpoint(boost::asio::ip::address_v4::loopback(), 0));
    int opened = 0;
    listener->Listen([&](auto) { ++opened; }, [](auto) {}, [](auto, carla::Buffer) {});
    ASSERT_EQ(io.poll_one(), 1u);
    boost::asio::ip::tcp::socket peer(io);
    peer.connect(listener->GetLocalEndpoint());
    // Finish accept, leaving the separately posted Open callback pending.
    ASSERT_EQ(io.run_one(), 1u);
    listener->Stop();
    EXPECT_NO_THROW(listener->Stop());
    // No worker is running here; unlike production Stop, this may restart
    // the context solely to drain canceled callbacks and verify their effect.
    io.restart();
    EXPECT_LE(io.poll(), 5u);
    EXPECT_EQ(opened, 0);
  }
}

TEST(multigpu_shutdown, live_connection_still_opens) {
  boost::asio::io_context io;
  auto listener = std::make_shared<Listener>(io,
      Listener::endpoint(boost::asio::ip::address_v4::loopback(), 0));
  int opened = 0;
  listener->Listen([&](auto) { ++opened; }, [](auto) {}, [](auto, carla::Buffer) {});
  ASSERT_EQ(io.poll_one(), 1u);
  boost::asio::ip::tcp::socket peer(io);
  peer.connect(listener->GetLocalEndpoint());
  ASSERT_EQ(io.run_one(), 1u);
  io.poll();
  EXPECT_EQ(opened, 1);
  listener->Stop();
}
