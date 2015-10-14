---
layout: docs
title: Functions
short_title: Functions
---

## force_ask 
code: |
  if user.address.address and retry_address:
    retry_address = False
    force_ask('user.address.address')
comment: |
  This is an example of how the "force_ask" function can be used to
  ask a question that has already been asked.
