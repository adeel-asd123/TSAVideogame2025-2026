/**
 * PANDA 3D SOFTWARE
 * Copyright (c) Carnegie Mellon University.  All rights reserved.
 *
 * All use of this software is subject to the terms of the revised BSD
 * license.  You should have received a copy of this license along
 * with this source code in a file named "LICENSE."
 *
 * @file simpleFuture.h
 * @author rdb
 * @date 2025-01-22
 */

#ifndef SIMPLEFUTURE_H
#define SIMPLEFUTURE_H

#if 0

#include "pandabase.h"
#include "completionCounter.h"

/**
 * Simple future class with an optional callback function to run on completion.
 * The usual way to use this is to create a CompletionCounter, call make_token()
 * on it to get one or more CompletionToken objects, pass those off to some
 * async work and call complete() on them when they are done.  When the last
 * complete() call is made, the future's callback is triggered.  If all tokens
 * pass true to complete(), the future is called with a true argument, otherwise
 * it is called with a false argument.
 *
 * To register a callback, call then(), which consumes the future.  At the
 * moment, only one callback may be registered.
 *
 * At the moment, no result value may be returned, but this could be added in
 * the future via a template argument.
 */
class EXPCL_PANDA_PIPELINE SimpleFuture {
private:
  constexpr SimpleFuture() = default;

public:
  INLINE SimpleFuture(CompletionCounter &&counter) noexcept;
  SimpleFuture(const SimpleFuture &copy) = delete;
  INLINE SimpleFuture(SimpleFuture &&from) noexcept;

  INLINE ~SimpleFuture();

  INLINE static SimpleFuture failure();

  INLINE bool done() const;
  INLINE bool failed() const;

  template<class Callable>
  INLINE void then(Callable callable) &&;

  INLINE bool wait();

protected:
  CompletionState *_state = nullptr;
};

#include "simpleFuture.I"
#endif
#endif
