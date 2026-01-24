/**
 * PANDA 3D SOFTWARE
 * Copyright (c) Carnegie Mellon University.  All rights reserved.
 *
 * All use of this software is subject to the terms of the revised BSD
 * license.  You should have received a copy of this license along
 * with this source code in a file named "LICENSE."
 *
 * @file glStagingBuffer_src.h
 * @author rdb
 * @date 2025-01-20
 */

#include "pandabase.h"
#include "stagingBuffer.h"

#ifndef OPENGLES_1
/**
 *
 */
class EXPCL_GL CLP(StagingBuffer) : public StagingBuffer {
public:
  INLINE CLP(StagingBuffer)(CLP(GraphicsStateGuardian) *glgsg,
                           void *ptr, size_t size);

  ~CLP(StagingBuffer)();

  // This is the GL "name" of the data object.
  GLuint _index;

public:
  static TypeHandle get_class_type() {
    return _type_handle;
  }
  static void init_type() {
    StagingBuffer::init_type();
    register_type(_type_handle, CLASSPREFIX_QUOTED "StagingBuffer",
                  StagingBuffer::get_class_type());
  }
  virtual TypeHandle get_type() const {
    return get_class_type();
  }
  virtual TypeHandle force_init_type() {init_type(); return get_class_type();}

private:
  static TypeHandle _type_handle;
};

#include "glStagingBuffer_src.I"

#endif  // OPENGLES_1
