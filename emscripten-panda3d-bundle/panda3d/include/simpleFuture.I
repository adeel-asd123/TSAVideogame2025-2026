/**
 * PANDA 3D SOFTWARE
 * Copyright (c) Carnegie Mellon University.  All rights reserved.
 *
 * All use of this software is subject to the terms of the revised BSD
 * license.  You should have received a copy of this license along
 * with this source code in a file named "LICENSE."
 *
 * @file simpleFuture.I
 * @author rdb
 * @date 2025-01-22
 */

/**
 *
 */
INLINE SimpleFuture::
SimpleFuture(CompletionCounter &&counter) noexcept :
  _state(counter._state) {
  counter._state = nullptr;
}

/**
 *
 */
INLINE SimpleFuture::
SimpleFuture(SimpleFuture &&from) noexcept :
  _state(from._state) {
  from._state = nullptr;
}

/**
 *
 */
INLINE SimpleFuture::
~SimpleFuture() {
  if (_state != nullptr) {
    _state->unref();
  }
}

/**
 * Returns a future that already failed.
 */
INLINE SimpleFuture SimpleFuture::
failure() {
  return SimpleFuture();
}

/**
 * Returns true if the future was done.
 */
INLINE bool SimpleFuture::
done() const {
  CompletionState *state = _state;
  return state == nullptr ||
    (state->_counter.load(std::memory_order_acquire) & 0xffff) == 0;
}

/**
 * Returns true if the future has already failed.
 */
INLINE bool SimpleFuture::
failed() const {
  CompletionState *state = _state;
  return state == nullptr ||
    (state->_counter.load(std::memory_order_acquire) & ~0xffff) != 0;
}

/**
 * Runs the given callback immediately upon completion.  If the future is
 * already done, runs it immediately.  This requires an rvalue because it
 * consumes the future, use std::move() if you don't have an rvalue.
 *
 * The callback will either be called immediately or directly when the last
 * token calls complete(), however, it may also be called if a token is
 * destroyed.  This may happen at unexpected times, such as when the lambda
 * holding the token is destroyed prematurely.  In this case, however, the
 * passed success argument will always be false.
 */
template<class Callable>
INLINE void SimpleFuture::
then(Callable callable) && {
  bool success = false;
  CompletionState *state = _state;
  if (state != nullptr) {
    _state = nullptr;

    auto prev_value = state->_counter.load(std::memory_order_acquire);
    if ((prev_value & 0xffff) != 0) {
      // Not yet done.
      std::cerr << "not yet done\n";
      nassertv(!state->_callback);
      state->_callback = std::move(callable);

      prev_value = state->_counter.fetch_sub(1, std::memory_order_release);
      if (UNLIKELY((prev_value & 0xffff) == 0)) {
        // Became done in the meantime.  Run the callback in-place.
        std::cerr << "became done\n";
        state->_callback((prev_value & ~0xffff) == 0);
        delete state;
      }
      return;
    }

    nassertv(!state->_callback);
    success = (prev_value & ~0xffff) == 0;
    std::cerr << "done at time of then(), value is " << std::hex << prev_value << std::dec << ", success=" << success << "\n";
    delete state;
  }

  // Already done, so call the callback.
  callable(success);
}

/**
 * Waits synchronously for the future to be done.  Returns true if the future
 * succeeded, false if it set the error flag.
 */
INLINE bool SimpleFuture::
wait() {
  CompletionState *state = _state;
  nassertr(state != nullptr && !state->_callback, false);

  struct Result {
    patomic_flag done = ATOMIC_FLAG_INIT;
    bool success;
  } result;

  _state->_callback = [&](bool success) {
    result.done.test_and_set();
    result.done.notify_one();
    result.success = success;
  };
  _state->unref();
  _state = nullptr;

  result.done.wait(false);
  return result.success;
}
