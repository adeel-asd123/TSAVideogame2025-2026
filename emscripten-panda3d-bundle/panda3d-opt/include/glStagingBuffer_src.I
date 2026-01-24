/**
 * PANDA 3D SOFTWARE
 * Copyright (c) Carnegie Mellon University.  All rights reserved.
 *
 * All use of this software is subject to the terms of the revised BSD
 * license.  You should have received a copy of this license along
 * with this source code in a file named "LICENSE."
 *
 * @file glStagingBuffer_src.I
 * @author rdb
 * @date 2025-01-20
 */

/**
 *
 */
INLINE CLP(StagingBuffer)::
CLP(StagingBuffer)(CLP(GraphicsStateGuardian) *glgsg, void *data, size_t size) :
  StagingBuffer(glgsg, data, size),
  _index(0)
{
}
